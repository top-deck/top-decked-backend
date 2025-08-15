from fastapi import APIRouter, UploadFile, Depends
from sqlmodel import text
from typing import Annotated
from app.utils.TorneioUtil import importar_torneio, retornar_torneio_completo, editar_torneio_regras, calcular_pontuacao
from app.schemas.Torneio import TorneioPublico, TorneioAtualizar
from app.models import Torneio, TorneioBase, JogadorTorneioLink, Jogador
from app.core.db import SessionDep
from app.core.exception import TopDeckedException
from app.core.security import TokenData
from app.dependencies import retornar_loja_atual, retornar_jogador_atual
from sqlmodel import select


router = APIRouter(
    prefix="/lojas/torneios",
    tags=["Torneios"])


@router.post("/importar", response_model=TorneioPublico)
def importar_torneios(session: SessionDep, arquivo: UploadFile, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = importar_torneio(session, arquivo, loja.id)
    session.refresh(torneio)

    torneio_completo = retornar_torneio_completo(torneio)
    return torneio_completo


@router.post("/{torneio_id}/importar", response_model=TorneioPublico)
def importar_torneios(session: SessionDep, arquivo: UploadFile, torneio_id: str, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = session.get(Torneio, torneio_id)

    if not torneio:
        raise TopDeckedException.not_found("Torneio não existe")
    if not torneio.loja_id == loja.id:
        raise TopDeckedException.forbidden()
        
    torneio = importar_torneio(session, arquivo, loja.id, torneio)
    session.refresh(torneio)

    torneio_completo = retornar_torneio_completo(torneio)
    return torneio_completo


@router.put("/{torneio_id}", response_model=TorneioPublico)
def editar_torneio(session: SessionDep, 
                   torneio_id: str, 
                   torneio_atualizar: TorneioAtualizar, 
                   loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneio = session.get(Torneio, torneio_id)
    
    if not torneio:
        TopDeckedException.not_found("Torneio não existe")
    if not torneio.loja_id == loja.id:
        TopDeckedException.forbidden()
        
    dados_para_atualizar = torneio_atualizar.model_dump(
            exclude={"regras_adicionais"}, exclude_unset=True)
    
    torneio.sqlmodel_update(dados_para_atualizar)
    session.add(torneio)
    
    if torneio.regra_basica or torneio.regras_adicionais:
        torneio = editar_torneio_regras(torneio, 
                                        torneio_atualizar.regra_basica_id, 
                                        torneio_atualizar.regras_adicionais)
    
        session.add(torneio)
        calcular_pontuacao(session, torneio)
    
    session.commit()
    session.refresh(torneio)
    return retornar_torneio_completo(torneio)


@router.delete("/", status_code=204)
def deletar_torneios(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    session.exec(text("DELETE FROM rodada"))
    session.exec(text("DELETE FROM jogadortorneiolink"))
    session.exec(text("DELETE FROM torneio"))
    session.commit()

@router.post("/criar",response_model=TorneioPublico)
def criar_torneio(session:SessionDep, torneio: TorneioBase, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    novo_torneio = Torneio(
        **torneio.model_dump(),
        loja_id = loja.id,
    )
    session.add(novo_torneio)
    session.commit()
    session.refresh(novo_torneio)
    return retornar_torneio_completo(novo_torneio)

@router.get("/", response_model=list[TorneioPublico])
def get_torneios(session: SessionDep):
    torneios = session.exec(select(Torneio))
    return [retornar_torneio_completo(torneio) for torneio in torneios]

@router.get("/loja", response_model=list[TorneioPublico])
def get_loja_torneios(session: SessionDep, loja: Annotated[TokenData, Depends(retornar_loja_atual)]):
    torneios = session.exec(select(Torneio).where(
        Torneio.loja_id == loja.id
    )).all()
    
    if not torneios:
        raise TopDeckedException.not_found("Nenhum torneio encontrado.")
    return [retornar_torneio_completo(torneio) for torneio in torneios]

@router.get("/{torneio_id}", response_model=TorneioPublico)
def get_torneio_por_id(
    torneio_id: str,
    session: SessionDep,
    loja: Annotated[TokenData, Depends(retornar_loja_atual)]
):
    torneio = session.exec(select(Torneio).where(
        Torneio.id == torneio_id,
        Torneio.loja_id == loja.id
    )).first()

    if not torneio:
        raise TopDeckedException.not_found("Torneio não encontrado.")

    return retornar_torneio_completo(torneio)

@router.post("/{torneio_id}/inscricao", response_model=JogadorTorneioLink)
def inscrever_jogador(session: SessionDep, torneio_id: str, token_data: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    torneio = session.get(Torneio, torneio_id)
    jogador = session.get(Jogador, token_data.id)
    
    if not torneio:
        raise TopDeckedException.not_found("Torneio não existe")
    if torneio.finalizado:
        raise TopDeckedException.bad_request("Torneio já finalizado")
    if not jogador.pokemon_id:
        raise TopDeckedException.bad_request("Jogador não possui um Pokémon ID vinculado")
    
    inscricao = JogadorTorneioLink(
        jogador_id=jogador.pokemon_id,
        torneio_id=torneio.id,
        regra_basica_id=torneio.regra_basica_id if torneio.regra_basica_id else None,
    )
    
    session.add(inscricao)
    session.commit()
    session.refresh(inscricao)

    return inscricao

@router.delete("/{torneio_id}/inscricao", status_code=204)
def desinscrever_jogador(session: SessionDep, torneio_id: str, token_data: Annotated[TokenData, Depends(retornar_jogador_atual)]):
    torneio = session.get(Torneio, torneio_id)
    jogador = session.get(Jogador, token_data.id)

    if not torneio:
        raise TopDeckedException.not_found("Torneio não existe")
    if torneio.finalizado:
        raise TopDeckedException.bad_request("Torneio já finalizado")

    inscricao = session.exec(select(JogadorTorneioLink).where(
        JogadorTorneioLink.jogador_id == jogador.pokemon_id,
        JogadorTorneioLink.torneio_id == torneio.id
    )).first()

    if not inscricao:
        raise TopDeckedException.not_found("Inscrição não encontrada")

    session.delete(inscricao)
    session.commit()