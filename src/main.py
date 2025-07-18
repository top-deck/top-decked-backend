from fastapi import FastAPI
from fastapi.routing import APIRoute

from src.api.main import api_router
from src.core import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
app.include_router(api_router)

