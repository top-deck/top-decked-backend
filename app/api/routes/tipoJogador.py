from app.core.db import SessionDep
from app.models.TipoJogador import TipoJogador
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.api.routes.login import retornar_usuario_atual, TokenData

from app.models.TipoJogador import TipoJogadorBase, TipoJogador, TipoJogadorPublico

router = APIRouter(
    prefix="/lojas/tipoJogador",
    tags=["Tipo de Jogador"])

@router.post("/", response_model=TipoJogadorPublico)
def criar_tipo_jogador(session: SessionDep, tipo_jogador: TipoJogadorBase, usuario: Annotated[TokenData, Depends(retornar_usuario_atual)]):
    if usuario.tipo != "loja":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas lojas podem criar tipos de jogador.")
    
    novo_tipo_jogador = TipoJogador(
        **tipo_jogador.dict(), 
        loja=usuario.id
    )
    
    session.add(novo_tipo_jogador)
    session.commit()
    session.refresh(novo_tipo_jogador)
    return novo_tipo_jogador

@router.get("/", response_model=list[TipoJogadorPublico])
def get_tipos_jogador(session: SessionDep, usuario: Annotated[TokenData, Depends(retornar_usuario_atual)]):
    tipos = session.query(TipoJogador).filter(
        TipoJogador.loja == usuario.id
    ).all()
    if not tipos:
        raise HTTPException(status_code=404, detail="Nenhum tipo de jogador encontrado.")
    return tipos

@router.get("/{tipo_id}", response_model=TipoJogadorPublico)
def get_tipo_jogador_por_id(
    tipo_id: int,
    session: SessionDep,
    usuario: Annotated[TokenData, Depends(retornar_usuario_atual)]
):
    tipo = session.query(TipoJogador).filter(
        TipoJogador.id == tipo_id,
        TipoJogador.loja == usuario.id
    ).first()

    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de jogador não encontrado.")

    return tipo

@router.delete("/{tipo_id}", status_code=204)
def delete_tipo_jogador(
    tipo_id: int,
    session: SessionDep,
    usuario: Annotated[TokenData, Depends(retornar_usuario_atual)]
):
    tipo = session.query(TipoJogador).filter(
        TipoJogador.id == tipo_id,
        TipoJogador.loja == usuario.id
    ).first()

    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de jogador não encontrado.")

    session.delete(tipo)
    session.commit()