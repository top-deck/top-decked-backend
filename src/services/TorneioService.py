from src.core.db import SessionDep
from fastapi import HTTPException, UploadFile
from sqlmodel import select
from sqlalchemy import func
from src.core.security import oauth2_scheme

import xml.etree.ElementTree as ET
from datetime import datetime
from src.models.Torneio import Torneio


def importar_torneio(session: SessionDep, arquivo: UploadFile):
    dados = arquivo.file.read()
    try:
        xml = ET.fromstring(dados)
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Arquivo XML inválido")

    torneio = Torneio()
    _importar_metadados(xml, torneio)

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


def _importar_rodadas(xml: ET.Element, torneio: Torneio):
    