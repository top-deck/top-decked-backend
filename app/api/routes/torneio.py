from fastapi import APIRouter, UploadFile, Depends
from sqlmodel import text
from typing import Annotated
from app.services.TorneioService import importar_torneio

from app.models.Torneio import Torneio
from app.core.db import SessionDep
from app.core.security import TokenData
from dependencies import retornar_loja_atual

router = APIRouter(
    prefix="/lojas/torneios",
    tags=["Torneios"])


@router.post("/importar", response_model=Torneio)
def importar_torneios(session: SessionDep, arquivo: UploadFile, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = importar_torneio(session, arquivo, loja.id)
    session.add(torneio)
    session.commit()
    session.refresh(torneio)
    return torneio


@router.delete("/", status_code=204)
def deletar_torneios(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    session.exec(text("DELETE FROM rodada"))
    session.exec(text("DELETE FROM jogadortorneiorelacao"))
    session.exec(text("DELETE FROM torneio"))
    session.commit()
