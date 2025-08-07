from app.core.db import SessionDep
from app.models.TipoJogador import TipoJogador
from fastapi import APIRouter, Depends
from app.core.exception import EXCEPTIONS
from typing import Annotated
from app.core.security import TokenData
from app.dependencies import retornar_loja_atual
from app.models.TipoJogador import TipoJogadorBase, TipoJogador, TipoJogadorPublico
from sqlmodel import select


router = APIRouter(
    prefix="/lojas/tipoJogador",
    tags=["Tipo de Jogador"])

@router.post("/", response_model=TipoJogadorPublico)
def criar_tipo_jogador(session: SessionDep, tipo_jogador: TipoJogadorBase, 
                       loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    
    novo_tipo_jogador = TipoJogador(
        **tipo_jogador.model_dump(), 
        loja=loja.id
    )
    
    session.add(novo_tipo_jogador)
    session.commit()
    session.refresh(novo_tipo_jogador)
    return novo_tipo_jogador

@router.get("/", response_model=list[TipoJogadorPublico])
def get_tipos_jogador(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    tipos = session.exec(select(TipoJogador).where(
        TipoJogador.loja == loja.id
    )).all()
    
    if not tipos:
        raise EXCEPTIONS.not_found("Nenhum tipo de jogador encontrado.")
    return tipos

@router.get("/{tipo_id}", response_model=TipoJogadorPublico)
def get_tipo_jogador_por_id(
    tipo_id: int,
    session: SessionDep,
    loja: Annotated[TokenData, Depends(retornar_loja_atual)]
):
    tipo = session.exec(select(TipoJogador).where(
        TipoJogador.id == tipo_id,
        TipoJogador.loja == loja.id
    )).first()

    if not tipo:
        raise EXCEPTIONS.not_found("Tipo de jogador não encontrado.")

    return tipo

@router.delete("/{tipo_id}", status_code=204)
def delete_tipo_jogador(
    tipo_id: int,
    session: SessionDep,
    loja: Annotated[TokenData, Depends(retornar_loja_atual)]
):
    tipo = session.exec(select(TipoJogador).where(
        TipoJogador.id == tipo_id,
        TipoJogador.loja == loja.id
    )).first()

    if not tipo:
        raise EXCEPTIONS.not_found("Tipo de jogador não encontrado.")

    session.delete(tipo)
    session.commit()