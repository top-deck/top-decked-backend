from fastapi import APIRouter, UploadFile, Depends
from sqlmodel import text, select
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.utils.TorneioUtil import importar_torneio, retornar_torneio_completo, editar_torneio_regras
from app.schemas.Torneio import TorneioPublico, TorneioAtualizar
from app.models import Torneio
from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.core.security import TokenData
from app.dependencies import retornar_loja_atual

router = APIRouter(
    prefix="/lojas/torneios",
    tags=["Torneios"])


@router.post("/importar", response_model=TorneioPublico)
def importar_torneios(session: SessionDep, arquivo: UploadFile, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = importar_torneio(session, arquivo, loja.id)
    session.refresh(torneio)

    torneio_completo = retornar_torneio_completo(session, torneio)
    return torneio_completo


@router.put("/{torneio_id}", response_model=TorneioPublico)
def editar_torneio(session: SessionDep, 
                   torneio_id: str, 
                   torneio_atualizar: TorneioAtualizar, 
                   loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = session.exec(select(Torneio).where(Torneio.id == torneio_id)).first()
    
    if not torneio:
        TopDeckedException.not_found("Torneio não existe")
    if not torneio.loja_id == loja.id:
        TopDeckedException.forbidden

    return editar_torneio_regras(session, torneio, torneio_atualizar)


@router.delete("/", status_code=204)
def deletar_torneios(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    session.exec(text("DELETE FROM rodada"))
    session.exec(text("DELETE FROM jogadortorneiolink"))
    session.exec(text("DELETE FROM torneio"))
    session.commit()
