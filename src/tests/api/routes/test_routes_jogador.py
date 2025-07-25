from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.tests.db.config import app
from src.core.db import get_session


client = TestClient(app)

def test_retornar_jogador_sem_jogador() -> None:
    r = client.get(f"/jogadores")
    assert r.status_code == 200
    assert r.json() == []