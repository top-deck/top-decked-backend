from fastapi import APIRouter
from src.api.routes import loja, jogador, login, torneio


api_router = APIRouter()

api_router.include_router(jogador.router)
api_router.include_router(loja.router)
api_router.include_router(login.router)
api_router.include_router(torneio.router)
