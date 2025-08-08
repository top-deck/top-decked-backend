from dotenv import load_dotenv

load_dotenv(override=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.api.main import api_router
from app.core.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)