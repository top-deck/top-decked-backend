from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app
# from app.core.config import settings
# from app.crud import create_user
# from app.models import UserCreate

client = TestClient(app)

def test_retornar_jogador_sem_jogador() -> None:
    r = client.get(f"/jogadores")
    assert r.status_code == 404
