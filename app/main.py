from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.main import api_router
from app.core.db import create_db_and_tables

from dotenv import load_dotenv

load_dotenv(override=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


    
app.include_router(api_router)
