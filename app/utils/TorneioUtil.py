from fastapi import UploadFile
from sqlmodel import select
import xml.etree.ElementTree as ET
from datetime import datetime

from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.models import Rodada, Torneio, Jogador, JogadorTorneioLink


def importar_torneio(session: SessionDep, arquivo: UploadFile, loja_id: int, torneio: Torneio = None):
    dados = arquivo.file.read()
    try:
        xml = ET.fromstring(dados)
    except ET.ParseError:
        raise TopDeckedException.bad_request("Arquivo XML inválido")
    
    if torneio:
        session.delete(torneio)
    torneio = _importar_metadados(xml, loja_id)
    session.add(torneio)
    session.commit()
    session.refresh(torneio)

    jogadores = _importar_jogadores(xml, session)
    
    for jogador in jogadores:
        _criar_relacao_jogador_torneio(jogador.pokemon_id, torneio.id, session)

    _importar_rodadas(xml, torneio.id, session)
    
    return torneio


def _importar_metadados(xml: ET.Element, loja_id: int):
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
    participacao = JogadorTorneioLink(
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


def retornar_torneio_completo(torneio: Torneio):
    torneio_dict = torneio.model_dump()
    
    torneio_dict["loja"] = torneio.loja
    torneio_dict["jogadores"] = [
        {
            "jogador_id": link.jogador_id,
            "nome": link.jogador.nome,
            "tipo_jogador_id": link.tipo_jogador_id,
            "pontuacao": link.pontuacao
        }
        for link in torneio.jogadores
    ]

    torneio_dict["rodadas"] = [
        {
            "jogador1_id": rodada.jogador1_id,
            "jogador2_id": rodada.jogador2_id,
            "vencedor": rodada.vencedor,
            "num_rodada": rodada.num_rodada,
            "mesa": rodada.mesa,
            "data_de_inicio": rodada.data_de_inicio
        }
        for rodada in torneio.rodadas
    ]

    
    return torneio_dict


def editar_torneio_regras(torneio: Torneio, regra_basica: int, regras_adicionais: dict):
    torneio.regra_basica_id = regra_basica
    
    for jogador in torneio.jogadores:
        jogador.pontuacao = 0
        jogador.pontuacao_com_regras = 0
        jogador_id = jogador.jogador_id
        
        if jogador_id in regras_adicionais:
            jogador.tipo_jogador_id = regras_adicionais[jogador_id]
        else:
            jogador.tipo_jogador_id = regra_basica
    
    return torneio


def calcular_pontuacao(session: SessionDep, torneio: Torneio):
    regra_basica = torneio.regra_basica
    
    for rodada in torneio.rodadas:
        jogador1_id = rodada.jogador1_id
        jogador2_id = rodada.jogador2_id
        jogador1_link = session.get(JogadorTorneioLink, {"torneio_id": torneio.id,
                                                          "jogador_id": jogador1_id})
        jogador2_link = session.get(JogadorTorneioLink, {"torneio_id": torneio.id,
                                                          "jogador_id": jogador2_id})
        jogador1_tipo = jogador1_link.tipo_jogador
        jogador2_tipo = jogador2_link.tipo_jogador

        if rodada.vencedor == jogador1_id:
            # Jogador 1 ganha os pontos por vitória 
            # e os pontos da regra de derrota do oponente
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_vitoria 
                                                + jogador2_tipo.pt_oponente_ganha)
            # Jogador 2 ganha os pontos por derrota 
            # e os pontos da regra de vitória do oponente (possivelmente negativos)
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_derrota
                                                + jogador1_tipo.pt_oponente_perde)

            jogador1_link.pontuacao += (regra_basica.pt_vitoria
                                           + regra_basica.pt_oponente_ganha)
            
            jogador2_link.pontuacao += (regra_basica.pt_derrota
                                            + regra_basica.pt_oponente_perde)
            
        elif rodada.vencedor == jogador2_id:
            # Jogador 2 ganha os pontos por vitória
            # e os pontos da regra de derrota do oponente
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_vitoria
                                        + jogador1_tipo.pt_oponente_ganha)
            # Jogador 1 ganha os pontos por derrota
            # e os pontos da regra de vitória do oponente (possivelmente negativos)
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_derrota
                                                + jogador2_tipo.pt_oponente_perde)
            
            jogador2_link.pontuacao += (regra_basica.pt_vitoria
                                                   + regra_basica.pt_oponente_ganha)
            
            jogador1_link.pontuacao += (regra_basica.pt_derrota
                                        + regra_basica.pt_oponente_perde)
        else:
            # Jogador 1 ganha os pontos por empate
            # e os pontos da regra de empate do oponente
            jogador1_link.pontuacao_com_regras += (jogador1_tipo.pt_empate
                                                + jogador2_tipo.pt_oponente_empate)
            # Jogador 2 ganha os pontos por empate
            # e os pontos da regra de empate do oponente
            jogador2_link.pontuacao_com_regras += (jogador2_tipo.pt_empate
                                                + jogador1_tipo.pt_oponente_empate)
            
            jogador1_link.pontuacao_com_regras += (regra_basica.pt_empate
                                                   + regra_basica.pt_oponente_empate)
            
            jogador2_link.pontuacao_com_regras += (regra_basica.pt_empate
                                                   + regra_basica.pt_oponente_empate)
            
    jogador1_link.pontuacao_com_regras += torneio.pontuacao_de_participacao
    jogador2_link.pontuacao_com_regras += torneio.pontuacao_de_participacao
    session.add(jogador1_link)
    session.add(jogador2_link)
    
def calcular_taxa_vitoria(session: SessionDep, jogador: Jogador):
    vitorias, derrotas, empates = 0, 0, 0
    
    rodadas = session.exec(
                ((Rodada.jogador1_id == jogador.pokemon_id) or (Rodada.jogador2_id == jogador.pokemon_id)))

    for rodada in rodadas:
        if(rodada.vencedor == jogador.pokemon_id):
            vitorias += 1
        elif(rodada.vencedor is not None):
            derrotas += 1
        else:
            empates += 1
            
    total = vitorias + derrotas + empates
    return int((vitorias / total) * 100) if total > 0 else 0