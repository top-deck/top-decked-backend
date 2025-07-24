from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute

from api.main import api_router
from core import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


    
app.include_router(api_router)
