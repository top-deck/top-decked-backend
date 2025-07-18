from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.models import Jogador, JogadorPublico, JogadorUpdate, JogadorCriar
from src.core import SessionDep

router = APIRouter(tags=["Jogadores"])

@router.post("/jogadores/", response_model=JogadorPublico)
def create_jogador(jogador: JogadorCriar, session: SessionDep):
    existing_jogador = session.exec(select(Jogador).where(Jogador.email == jogador.email)).first()
    if existing_jogador:
        raise HTTPException(status_code=400, detail="Email ja registrado")
    novo_jogador = Jogador.from_orm(jogador)
    session.add(novo_jogador)
    session.commit()
    session.refresh(novo_jogador)
    return novo_jogador

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