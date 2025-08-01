from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException, File, UploadFile
from sqlmodel import select
from src.services.TorneioService import importar_torneio


from src.models.Torneio import Torneio
from src.core.db import SessionDep

router = APIRouter(tags=["Torneios"])


@router.post("/torneios/importar", response_model=Torneio)
def importar_torneios(arquivo: UploadFile, session: SessionDep):
    torneio = importar_torneio(session, arquivo)
    session.add(torneio)
    session.commit()
    session.refresh(torneio)
    return torneio