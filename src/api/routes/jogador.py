from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from models import Jogador, JogadorPublico, JogadorUpdate, JogadorCriar
from core import SessionDep
from models.Usuario import Usuario

router = APIRouter(tags=["Jogadores"])

@router.post("/jogadores/", response_model=JogadorPublico)
def create_jogador(jogador: JogadorCriar, session: SessionDep):
    novo_usuario = Usuario(
        email=jogador.usuario.email
    )
    novo_usuario.set_senha(jogador.usuario.senha)
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    db_jogador = Jogador(
        name=jogador.name,
        usuario_id=novo_usuario.id,
        usuario=novo_usuario
    )
    session.add(db_jogador)
    session.commit()
    session.refresh(db_jogador)
    return db_jogador

@router.get("/jogadores/{jogador_id}", response_model=JogadorPublico)
def read_jogador(jogador_id: int, session: SessionDep):
    jogador = session.get(Jogador, jogador_id)
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    return jogador

@router.get("/jogadores/", response_model=list[JogadorPublico])
def get_jogadores(session : SessionDep): 
    return session.exec(select(Jogador))
    
@router.put("/jogadores/{jogador_id}", response_model=JogadorPublico)
def update_jogador(jogador_id: int, jogador: JogadorUpdate, session: SessionDep):
    existing_jogador = session.get(Jogador, jogador_id)
    if not existing_jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    
    hero_data = jogador.model_dump(exclude_unset=True)
    existing_jogador.sqlmodel_update(hero_data)
    session.add(existing_jogador)
    session.commit()
    session.refresh(existing_jogador)
    return existing_jogador