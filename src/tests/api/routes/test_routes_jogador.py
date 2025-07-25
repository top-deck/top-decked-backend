from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.main import app
from src.core.db import get_session
# from app.core.config import settings
# from app.crud import create_user
# from app.models import UserCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

current_file_path = Path(__file__).resolve()

db_path = current_file_path.parents[2] / "db" / "test.db"
db_path.parent.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

def override_get_session():
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

def test_retornar_jogador_sem_jogador() -> None:
    r = client.get(f"/jogadores")
    assert r.status_code == 200
    assert r.json() == []
