from fastapi import APIRouter, UploadFile, Depends
from sqlmodel import text, select
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.utils.TorneioUtil import importar_torneio, retornar_torneio_completo

from app.models.Torneio import Torneio, TorneioPublico
from app.core.db import SessionDep
from app.core.security import TokenData
from app.dependencies import retornar_loja_atual

router = APIRouter(
    prefix="/lojas/torneios",
    tags=["Torneios"])


@router.post("/importar", response_model=TorneioPublico)
def importar_torneios(session: SessionDep, arquivo: UploadFile, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = importar_torneio(session, arquivo, loja.id)
    
    torneio_completo = retornar_torneio_completo(session, torneio)
    return torneio_completo


@router.delete("/", status_code=204)
def deletar_torneios(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    session.exec(text("DELETE FROM rodada"))
    session.exec(text("DELETE FROM jogadortorneiorelacao"))
    session.exec(text("DELETE FROM torneio"))
    session.commit()
