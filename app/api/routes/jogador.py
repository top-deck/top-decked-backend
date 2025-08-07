from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.models.Jogador import Jogador, JogadorPublico, JogadorUpdate, JogadorCriar
from app.core.db import SessionDep
from app.models.Usuario import Usuario
from app.services.UsuarioService import verificar_novo_usuario


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
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    return jogador

@router.get("/", response_model=list[JogadorPublico])
def get_jogadores(session : SessionDep): 
    return session.exec(select(Jogador)).all()
    
@router.put("/{jogador_id}", response_model=JogadorPublico)
def update_jogador(jogador_id: int, jogador: JogadorUpdate, session: SessionDep):
    existing_jogador = session.get(Jogador, jogador_id)
    if not existing_jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    if jogador.senha:
        existing_jogador.usuario.set_senha(jogador.senha)
        session.add(existing_jogador.usuario)
    jogador_data = jogador.model_dump(exclude_unset=True, exclude={"senha"})
    existing_jogador.sqlmodel_update(jogador_data)
    session.add(existing_jogador)
    session.commit()
    session.refresh(existing_jogador)
    return existing_jogador