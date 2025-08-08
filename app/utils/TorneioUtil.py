from sqlalchemy.exc import NoResultFound
from fastapi import UploadFile
from sqlmodel import select, update
import xml.etree.ElementTree as ET
from datetime import datetime

from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.models.Torneio import Torneio, TorneioPublico, TorneioAtualizar
from app.models.Jogador import Jogador, JogadorPublicoLoja
from app.models.JogadorTorneioRelacao import JogadorTorneioRelacao
from app.models.Rodada import Rodada


def importar_torneio(session: SessionDep, arquivo: UploadFile, loja_id: int):
    dados = arquivo.file.read()
    try:
        xml = ET.fromstring(dados)
    except ET.ParseError:
        raise TopDeckedException.bad_request("Arquivo XML inválido")

    torneio = _importar_metadados(xml, session, loja_id)
    session.add(torneio)
    session.commit()
    session.refresh(torneio)

    jogadores = _importar_jogadores(xml, session)
    
    for jogador in jogadores:
        _criar_relacao_jogador_torneio(jogador.pokemon_id, torneio.id, session)

    _importar_rodadas(xml, torneio.id, session)
    
    return torneio


def _importar_metadados(xml: ET.Element, session: SessionDep, loja_id: int):
    dados = xml.find("data")
    if dados is None:
        raise TopDeckedException.bad_request("Bloco 'data' não encontrado no XML")

    id = dados.findtext("id")
    nome = dados.findtext("name")
    cidade = dados.findtext("city")
    estado = dados.findtext("state")
    tempo_por_rodada = dados.findtext("roundtime", default="30")
    data_inicio_str = dados.findtext("startdate")
    
    if not cidade or not data_inicio_str:
        raise TopDeckedException.bad_request("Cidade ou data de início ausentes")

    try:
        data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
    except ValueError:
        raise TopDeckedException.bad_request("Data de início em formato inválido")
    descricao = f"{nome} {data_inicio}"

    return Torneio(id=id,
                   nome=nome,
                   descricao=descricao,
                   cidade=cidade,
                   estado=estado,
                   tempo_por_rodada=tempo_por_rodada,
                   data_inicio=data_inicio,
                   loja_id=loja_id,
                   finalizado=True)

def _importar_jogadores(xml: ET.Element, session: SessionDep):
    jogadores = []

    dados = xml.find("players")
    
    if dados is None:
        return jogadores
    
    for jogador in dados.findall("player"):
        pokemon_id = jogador.attrib.get("userid")
        primeiro_nome = jogador.findtext("firstname", "").strip()
        ultimo_nome = jogador.findtext("lastname", "").strip()
        nome = f"{primeiro_nome} {ultimo_nome}".strip()
        
        jogador_existente = session.exec(
            select(Jogador).where(Jogador.pokemon_id == pokemon_id)
        ).first()

        if jogador_existente:
            jogadores.append(jogador_existente)
        else:
            novo_jogador = Jogador(nome=nome, pokemon_id=pokemon_id)
            
            session.add(novo_jogador)
            session.commit()
            session.refresh(novo_jogador)
            
            jogadores.append(novo_jogador)

    return jogadores

def _criar_relacao_jogador_torneio(jogador_id: int, torneio_id: str, session: SessionDep):
    participacao = JogadorTorneioRelacao(
                    jogador_id=jogador_id,
                    torneio_id=torneio_id
                )
    
    session.add(participacao)
    session.commit()
    session.refresh(participacao)


def _importar_rodadas(xml: ET.Element, torneio_id: str, session: SessionDep):
    pods = xml.find("pods").findall("pod")
    rodadas = []
    for pod in pods:
        rodadas.extend(pod.find("rounds").findall("round"))
    
    for rodada in rodadas:
        num_rodada = int(rodada.get("number"))
        partidas = rodada.find("matches")
        
        _importar_partidas(partidas, torneio_id, num_rodada, session)

        
def _importar_partidas(partidas: ET.Element, torneio_id: str, num_rodada: int, session: SessionDep):
    partidas_criadas = []
    for partida in partidas.findall("match"):
        jogador1_id = partida.find("player1").get("userid")
        jogador2_id = partida.find("player2").get("userid")
        
        if jogador1_id is None or jogador2_id is None:
            continue
        vencedor = int(partida.get("outcome"))
        
        if vencedor == 1:
            vencedor = jogador1_id
        elif vencedor == 2:
            vencedor = jogador2_id
        else:
            vencedor = None
        
        mesa = int(partida.findtext("tablenumber"))
        
        timestamp_str = partida.findtext("timestamp")
        try:
            data_de_inicio = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S").date()
        except ValueError:
            raise TopDeckedException.bad_request("Data no formato inválido: {timestamp_str}")
        
        partida = Rodada(
            jogador1_id=jogador1_id,
            jogador2_id=jogador2_id,
                vencedor=vencedor,
                torneio_id=torneio_id,
                num_rodada=num_rodada,
                mesa=mesa,
                data_de_inicio=data_de_inicio
            )
        session.add(partida)
        session.commit()
        session.refresh(partida)
        partidas_criadas.append(partida)
        
    return partidas_criadas


# Refact
def retornar_torneio_completo(session: SessionDep, torneio: Torneio):
    query = (
        select(Jogador, JogadorTorneioRelacao.tipo_jogador_id)
        .join(JogadorTorneioRelacao, Jogador.pokemon_id == JogadorTorneioRelacao.jogador_id)
        .where(JogadorTorneioRelacao.torneio_id == torneio.id)
    )
    resultados = session.exec(query).all()

    jogadores_publicos = []
    for jogador, tipo_jogador_id in resultados:
        jogador_dict = jogador.model_dump()
        jogador_dict["tipo_jogador_id"] = tipo_jogador_id
        jogador_publico = JogadorPublicoLoja(**jogador_dict)
        jogadores_publicos.append(jogador_publico)

    torneio_completo = TorneioPublico(
        **torneio.model_dump(), jogadores=jogadores_publicos)

    return torneio_completo

# Refact
def editar_torneio_regras(session: SessionDep, torneio: Torneio, torneio_atualizar: TorneioAtualizar) -> Torneio:
    torneio.nome = torneio_atualizar.nome or torneio.nome
    torneio.descricao = torneio_atualizar.descricao or torneio.descricao
    torneio.cidade = torneio_atualizar.cidade or torneio.cidade
    torneio.estado = torneio_atualizar.estado or torneio.estado
    torneio.tempo_por_rodada = torneio_atualizar.tempo_por_rodada or torneio.tempo_por_rodada
    torneio.data_inicio = torneio_atualizar.data_inicio or torneio.data_inicio
    torneio.finalizado = torneio_atualizar.finalizado or torneio.finalizado

    session.add(torneio)
    session.commit()

    if torneio_atualizar.regras_adicionais:
        for jogador_id, tipo_jogador_id in torneio_atualizar.regras_adicionais.items():
            stmt = (
                update(JogadorTorneioRelacao)
                .where(JogadorTorneioRelacao.jogador_id == jogador_id)
                .where(JogadorTorneioRelacao.torneio_id == torneio.id)
                .values(tipo_jogador_id=tipo_jogador_id)
            )
            result = session.exec(stmt)
            if result.rowcount == 0:
                nova_relacao = JogadorTorneioRelacao(
                    jogador_id=jogador_id,
                    torneio_id=torneio.id,
                    tipo_jogador_id=tipo_jogador_id,
                )
                session.add(nova_relacao)

    session.commit()

    jogadores_no_torneio = session.exec(
        select(JogadorTorneioRelacao).where(
            JogadorTorneioRelacao.torneio_id == torneio.id)
    ).all()

    jogadores_com_regra_adicional = set(torneio_atualizar.regras_adicionais.keys(
    )) if torneio_atualizar.regras_adicionais else set()

    for relacao in jogadores_no_torneio:
        if relacao.jogador_id not in jogadores_com_regra_adicional:
            stmt = (
                update(JogadorTorneioRelacao)
                .where(JogadorTorneioRelacao.jogador_id == relacao.jogador_id)
                .where(JogadorTorneioRelacao.torneio_id == torneio.id)
                .values(tipo_jogador_id=torneio_atualizar.regra_basica)
            )
            session.exec(stmt)

    session.commit()
    session.refresh(torneio)
    
    torneio_completo = retornar_torneio_completo(session, torneio)
    return torneio_completo
