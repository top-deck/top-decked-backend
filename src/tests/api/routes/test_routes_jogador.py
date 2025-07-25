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

def test_criar_jogador() -> None:
    payload = {
        "nome": "João",
        "email": "joao@gmail.com",
        "senha": "senha123"
    }
    r = client.post("/jogadores/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["nome"] == "João"
    assert "id" in data


def test_criar_jogador_email_duplicado() -> None:
    payload = {
        "nome": "Maria",
        "email": "maria@gmail.com",
        "senha": "senha123"
    }
    client.post("/jogadores/", json=payload)  
    r = client.post("/jogadores/", json=payload) 
    assert r.status_code == 400
    assert "e-mail" in r.json()["detail"]

def test_ler_jogador_por_id() -> None:
    payload = {
        "nome": "Carlos",
        "email": "carlos@gmail.com",
        "senha": "senha123"
    }
    criar = client.post("/jogadores/", json=payload)
    jogador_id = criar.json()["id"]

    r = client.get(f"/jogadores/{jogador_id}")
    assert r.status_code == 200
    assert r.json()["nome"] == "Carlos"

def test_atualizar_jogador() -> None:
    payload = {
        "nome": "Ana",
        "email": "ana@gmail.com",
        "senha": "senha123"
    }
    criar = client.post("/jogadores/", json=payload)
    jogador_id = criar.json()["id"]

    update_payload = {
        "nome": "Ana Atualizada",
        "senha": "nova_senha"
    }

    r = client.put(f"/jogadores/{jogador_id}", json=update_payload)
    assert r.status_code == 200
    assert r.json()["nome"] == "Ana Atualizada"

def test_atualizar_jogador_inexistente() -> None:
    update_payload = {
        "nome": "Nao Existe",
        "senha": "123"
    }
    r = client.put("/jogadores/9999", json=update_payload)
    assert r.status_code == 404

def test_ler_jogador_inexistente() -> None:
    r = client.get("/jogadores/9999")
    assert r.status_code == 404

