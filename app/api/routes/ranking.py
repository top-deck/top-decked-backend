from fastapi import APIRouter, Query
from app.core.db import SessionDep
from app.schemas.Ranking import Ranking, RankingPorLoja
from app.utils.RankingUtil import calcula_ranking_geral, calcula_ranking_geral_por_loja
from typing import Annotated


router = APIRouter(
    prefix="/ranking",
    tags=["Ranking"])

@router.get("/geral", response_model=list[Ranking])
def get_ranking_geral(session: SessionDep):
    ranking = calcula_ranking_geral(session)
    return ranking

@router.get("/lojas", response_model=list[RankingPorLoja])
def get_ranking_geral_por_loja(session: SessionDep, mes: Annotated[int | None, Query(ge=1, le=12)] = None):
    ranking = calcula_ranking_geral_por_loja(session, mes)
    return ranking