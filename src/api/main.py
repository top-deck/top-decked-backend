from fastapi import APIRouter, FastAPI
from src.api.routes import routes_jogador, routes_loja
from src.core import create_db_and_tables


api_router = APIRouter()

api_router.include_router(routes_jogador.router)
api_router.include_router(routes_loja.router)
