from dotenv import load_dotenv
import os
load_dotenv(override=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.db import create_db_and_tables, inserir_cartas


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    inserir_cartas()
    yield


app = FastAPI(lifespan=lifespan)

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True) 
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
