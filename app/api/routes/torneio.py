from fastapi import APIRouter, UploadFile, Depends
from sqlmodel import text
from typing import Annotated
from app.utils.TorneioUtil import importar_torneio, retornar_torneio_completo, editar_torneio_regras, calcular_pontuacao
from app.schemas.Torneio import TorneioPublico, TorneioAtualizar
from app.models import Torneio, TorneioBase
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
            exclude={"regra_basica", "regras_adicionais"}, exclude_unset=True)
    
    torneio.sqlmodel_update(dados_para_atualizar)
    
    torneio_atualizado = editar_torneio_regras(torneio, 
                                               torneio_atualizar.regra_basica, 
                                               torneio_atualizar.regras_adicionais)
    session.add(torneio_atualizado)
    
    calcular_pontuacao(session, torneio_atualizado)
    
    session.commit()
    session.refresh(torneio_atualizado)
    
    return retornar_torneio_completo(torneio_atualizado)


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
    return novo_torneio