from src.core.db import SessionDep
from fastapi import HTTPException, UploadFile
from sqlmodel import select

import xml.etree.ElementTree as ET
from datetime import datetime
from src.models.Torneio import Torneio
from src.models.Jogador import Jogador
from src.models.JogadorTorneioRelacao import JogadorTorneioRelacao
from src.models.Rodada import Rodada


def importar_torneio(session: SessionDep, arquivo: UploadFile):
    dados = arquivo.file.read()
    try:
        xml = ET.fromstring(dados)
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Arquivo XML inválido")

    torneio = Torneio()
    _importar_metadados(xml, torneio)
    session.add(torneio)
    session.commit()
    session.refresh(torneio)

    jogadores = _importar_jogadores(xml, session)
    
    for jogador in jogadores:
        _criar_relacao_jogador_torneio(jogador.pokemon_id, torneio.id, session)

    _importar_rodadas(xml, torneio.id, session)
    
    return torneio


def _importar_metadados(xml: ET.Element, torneio: Torneio):
    dados = xml.find("data")
    if dados is None:
        raise HTTPException(
            status_code=400, detail="Bloco 'data' não encontrado no XML")

    id = dados.findtext("id")
    cidade = dados.findtext("city")
    estado = dados.findtext("state")
    tempo_por_rodada = dados.findtext("roundtime", default="30")
    data_inicio_str = dados.findtext("startdate")
    
    if not cidade or not data_inicio_str:
        raise HTTPException(
            status_code=400, detail="Cidade ou data de início ausentes")

    try:
        data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Data de início em formato inválido")

    torneio.id = id
    torneio.cidade = cidade
    torneio.estado = estado if estado else None
    torneio.tempo_por_rodada = int(tempo_por_rodada)
    torneio.data_inicio = data_inicio


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
    rodadas = xml.find("rounds")
    if rodadas is None:
        return
    
    for rodada in rodadas.findall("round"):
        num_rodada = int(rodada.get("number"))
        partidas = rodada.find("matches")
        
        partidas = _importar_partidas(partidas, torneio_id, num_rodada, session)

        
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
        
        mesa = partida.find("tablenumber")
        
        timestamp_str = partida.findtext("timestamp")
        try:
            data_de_inicio = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Data no formato inválido: {timestamp_str}")
        
        partida = Rodada(
            jogador1_id=jogador1_id,
            jogador2_id=jogador2_id,
                vencedor=vencedor,
                torneio_id=torneio_id,
                num_rodada=num_rodada,
                mesa=mesa,
                data_de_inicio=data_de_inicio
            )
        print("oi")
        session.add(partida)
        session.commit()
        session.refresh(partida)
        print("oii")
        partidas_criadas.append(partida)
        

    return partidas_criadas