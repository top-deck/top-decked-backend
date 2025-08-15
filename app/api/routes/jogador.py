from fastapi import APIRouter, Depends
from sqlmodel import select
from app.schemas.Jogador import JogadorPublico, JogadorUpdate, JogadorCriar
from app.core.db import SessionDep
from typing import Annotated
from app.core.security import TokenData
from app.core.exception import TopDeckedException
from app.core.security import TokenData
from app.models import Usuario, Jogador, JogadorTorneioLink
from app.utils.UsuarioUtil import verificar_novo_usuario
from app.utils.JogadorUtil import calcular_estatisticas
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

@router.get("/estatisticas")
def get_estatisticas(session: SessionDep,
                     token_data: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    jogador = session.get(Jogador, token_data.id)

    return calcular_estatisticas(session, jogador)

@router.get("/{jogador_id}", response_model=JogadorPublico)
def read_jogador(jogador_id: int, session: SessionDep):
    jogador = session.get(Jogador, jogador_id)
    if not jogador:
        raise TopDeckedException.not_found("Jogador nao encontrado")
    
    return jogador

@router.get("/", response_model=list[JogadorPublico])
def get_jogadores(session : SessionDep): 
    return session.exec(select(Jogador)).all()
    
@router.put("/", response_model=JogadorPublico)
def update_jogador(novo: JogadorUpdate, session: SessionDep, 
                   token_data : Annotated[TokenData, Depends(retornar_jogador_atual)]):
    jogador = session.get(Jogador, token_data.id)
    
    if not jogador:
        raise TopDeckedException.not_found("Jogador nao encontrado")
    
    if novo.senha:
        jogador.usuario.set_senha(novo.senha)
        session.add(jogador.usuario)
    
    if novo.pokemon_id:
        jogador_db = session.exec(select(Jogador)
                                  .where(Jogador.pokemon_id == novo.pokemon_id)).first()
        
        if jogador_db:
            jogador_db.nome = jogador.nome
            jogador_db.usuario_id = jogador.usuario_id
            session.delete(jogador)
            jogador = jogador_db
    
    jogador_data = novo.model_dump(exclude_unset=True, exclude={"senha"})
    jogador.sqlmodel_update(jogador_data)
    session.add(jogador)
    session.commit()
    session.refresh(jogador)
    return jogador

@router.delete("/{jogador_id}", status_code=204)
def delete_usuario(session: SessionDep,
                   jogador_id,
                   usuario: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    jogador = session.get(Jogador, jogador_id)
    
    if not jogador:
        raise TopDeckedException.not_found("Jogador não encontrado")
    
    if jogador.usuario_id != usuario.usuario_id:
        raise TopDeckedException.forbidden()
    
    session.delete(jogador.usuario)     
    session.commit()

@router.get("/torneios/inscritos", response_model=JogadorTorneioLink)
def torneios_inscritos(session: SessionDep,
                       token_data: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    jogador = session.get(Jogador, token_data.id)

    inscricoes = session.exec(select(JogadorTorneioLink)
                              .where(JogadorTorneioLink.jogador_id == jogador.pokemon_id)).all()
    
    if not inscricoes:
        raise TopDeckedException.not_found("Jogador não se inscreveu em nenhum torneio")
    
    return inscricoes