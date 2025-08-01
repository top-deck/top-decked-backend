from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException, File, UploadFile
from sqlmodel import select, text
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


@router.delete("/torneios", status_code=204)
def deletar_torneios(session: SessionDep):
    session.exec(text("DELETE FROM rodada"))
    session.exec(text("DELETE FROM jogadortorneiorelacao"))
    session.exec(text("DELETE FROM torneio"))
    session.commit()
