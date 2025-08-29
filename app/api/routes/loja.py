from fastapi import APIRouter, Depends
from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.schemas.Loja import LojaCriar, LojaPublico, LojaAtualizar
from app.models import Loja
from app.models import Usuario
from sqlmodel import select
from app.utils.UsuarioUtil import verificar_novo_usuario
from app.core.security import TokenData
from app.dependencies import retornar_loja_atual
from typing import Annotated


router = APIRouter(
    prefix="/lojas",
    tags=["Lojas"])

@router.post("/", response_model=LojaPublico)
def criar_loja(loja: LojaCriar, session: SessionDep):
    verificar_novo_usuario(loja.email, session)
    
    novo_usuario = Usuario(
        email=loja.email,
        tipo="loja"
    )
    novo_usuario.set_senha(loja.senha)
    
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    db_loja = Loja(
        nome=loja.nome,
        endereco=loja.endereco,
        telefone=loja.telefone,
        site=loja.site,
        usuario=novo_usuario
    )
    
    session.add(db_loja)
    session.commit()
    session.refresh(db_loja)

    return db_loja


@router.get("/", response_model=list[LojaPublico])
def retornar_lojas(session: SessionDep):
    lojas = session.exec(select(Loja))
    return lojas


@router.get("/{loja_id}", response_model=LojaPublico)
def retornar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise TopDeckedException.not_found("Loja não encontrada")
    return loja


@router.put("/", response_model=LojaPublico)
def atualizar_loja(token_data: Annotated[TokenData, Depends(retornar_loja_atual)], loja_atualizar: LojaAtualizar, session: SessionDep):
    loja_db = session.get(Loja, token_data.id)
    
    if not loja_db:
        raise TopDeckedException.not_found("Loja não encontrada")

    if loja_atualizar.email:
        loja_db.usuario.set_email(loja_atualizar.email, session)
    if loja_atualizar.senha:
        loja_db.usuario.set_senha(loja_atualizar.senha)
        
    session.add(loja_db.usuario)

    loja_data = loja_atualizar.model_dump(exclude_unset=True, exclude={"senha", "email"})
    loja_db.sqlmodel_update(loja_data)
    session.add(loja_db)
    session.commit()
    session.refresh(loja_db)
    
    return loja_db

@router.delete("/{loja_id}")
def apagar_loja(loja_id: int, session: SessionDep):
    loja = session.get(Loja, loja_id)
    if not loja:
        raise TopDeckedException.not_found("Loja não encontrada")
    session.delete(loja)
    session.commit()
    return {"ok": True}
