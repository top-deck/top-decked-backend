from fastapi import APIRouter
from app.api.routes import loja, jogador, login, torneio, tipoJogador, ranking


api_router = APIRouter()

api_router.include_router(jogador.router)
api_router.include_router(loja.router)
api_router.include_router(login.router)
api_router.include_router(torneio.router)
api_router.include_router(ranking.router)
api_router.include_router(tipoJogador.router)