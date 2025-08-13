from fastapi import APIRouter, Depends
from sqlmodel import select
from app.schemas.Jogador import JogadorPublico, JogadorUpdate, JogadorCriar
from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.core.security import TokenData
from app.models import Usuario, Jogador
from app.utils.UsuarioUtil import verificar_novo_usuario
from app.dependencies import retornar_jogador_atual
from typing import Annotated


router = APIRouter(
    prefix="/jogadores",
    tags=["Jogadores"])

@router.post("/", response_model=JogadorPublico)
def create_jogador(jogador: JogadorCriar, session: SessionDep):
    verificar_novo_usuario(jogador.email, session)


    novo_usuario = Usuario(
        email=jogador.email,
        tipo="jogador"
    )
    novo_usuario.set_senha(jogador.senha)
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    db_jogador = Jogador(
        nome=jogador.nome,
        usuario=novo_usuario
    )
    session.add(db_jogador)
    session.commit()
    session.refresh(db_jogador)
    return db_jogador

@router.get("/{jogador_id}", response_model=JogadorPublico)
def read_jogador(jogador_id: int, session: SessionDep):
    jogador = session.get(Jogador, jogador_id)
    if not jogador:
        raise TopDeckedException.not_found("Jogador nao encontrado")
    
    return jogador

@router.get("/", response_model=list[JogadorPublico])
def get_jogadores(session : SessionDep): 
    return session.exec(select(Jogador)).all()
    
@router.put("/{jogador_id}", response_model=JogadorPublico)
def update_jogador(jogador_id: int, jogador: JogadorUpdate, session: SessionDep):
    existing_jogador = session.get(Jogador, jogador_id)
    
    if not existing_jogador:
        raise TopDeckedException.not_found("Jogador nao encontrado")
    
    if jogador.senha:
        existing_jogador.usuario.set_senha(jogador.senha)
        session.add(existing_jogador.usuario)
    
    if jogador.pokemon_id:
        jogador_db = session.exec(select(Jogador)
                                  .where(Jogador.pokemon_id == jogador.pokemon_id)).first()
        
        if jogador_db:
            jogador_db.nome = existing_jogador.nome
            jogador_db.usuario_id = existing_jogador.usuario_id
            session.delete(existing_jogador)
            existing_jogador = jogador_db
    
    jogador_data = jogador.model_dump(exclude_unset=True, exclude={"senha"})
    existing_jogador.sqlmodel_update(jogador_data)
    session.add(existing_jogador)
    session.commit()
    session.refresh(existing_jogador)
    return existing_jogador


@router.delete("/{jogador_id}", status_code=204)
def delete_usuario(session: SessionDep,
                   jogador_id,
                   jogador_token: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    jogador = session.get(Jogador, jogador_id)

    if not jogador:
        raise TopDeckedException.not_found("Jogador não encontrado")

    if jogador_token.usuario_id != jogador.usuario_id:
        raise TopDeckedException.forbidden()

    session.delete(jogador)
    session.commit()