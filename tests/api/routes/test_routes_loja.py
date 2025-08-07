from fastapi.testclient import TestClient
from app.tests.db.config import app 

client = TestClient(app)

def test_retornar_lojas_vazio():
    r = client.get("/lojas/")
    assert r.status_code == 200
    assert r.json() == []

def test_criar_loja():
    payload = {
        "nome": "Loja Teste",
        "endereco": "Rua Teste, 123",
        "email": "loja_teste@gmail.com",
        "senha": "senha123"
    }
    r = client.post("/lojas/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["nome"] == "Loja Teste"
    assert "id" in data

def test_criar_loja_email_duplicado():
    payload = {
        "nome": "Loja Duplicada",
        "endereco": "Rua Duplicada, 456",
        "email": "loja_dup@gmail.com",
        "senha": "senha123"
    }
    client.post("/lojas/", json=payload)
    r = client.post("/lojas/", json=payload)
    assert r.status_code == 400
    assert "e-mail" in r.json()["detail"]

def test_buscar_loja_por_id():
    payload = {
        "nome": "Loja Para Buscar",
        "endereco": "Rua Busca, 789",
        "email": "loja_busca@gmail.com",
        "senha": "senha123"
    }
    criar = client.post("/lojas/", json=payload)
    loja_id = criar.json()["id"]

    r = client.get(f"/lojas/{loja_id}")
    assert r.status_code == 200
    assert r.json()["nome"] == "Loja Para Buscar"

def test_buscar_loja_inexistente():
    r = client.get("/lojas/999999")
    assert r.status_code == 404
    assert "não encontrada" in r.json()["detail"].lower()

def test_atualizar_loja():
    payload = {
        "nome": "Loja Atualizar",
        "endereco": "Rua Atualizar, 321",
        "email": "loja_update@gmail.com",
        "senha": "senha123"
    }
    criar = client.post("/lojas/", json=payload)
    loja_id = criar.json()["id"]

    update = {
        "nome": "Loja Atualizada",
        "endereco": "Rua Atualizada, 321",
        "senha": "nova_senha"
    }

    r = client.patch(f"/lojas/{loja_id}", json=update)
    assert r.status_code == 200
    data = r.json()
    assert data["nome"] == "Loja Atualizada"

def test_atualizar_loja_inexistente():
    r = client.patch("/lojas/999999", json={"nome": "Novo Nome"})
    assert r.status_code == 404

def test_deletar_loja():
    payload = {
        "nome": "Loja Deletar",
        "endereco": "Rua Deletar, 654",
        "email": "loja_del@gmail.com",
        "senha": "senha123"
    }
    criar = client.post("/lojas/", json=payload)
    loja_id = criar.json()["id"]

    r = client.delete(f"/lojas/{loja_id}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = client.get(f"/lojas/{loja_id}")
    assert r.status_code == 404

def test_deletar_loja_inexistente():
    r = client.delete("/lojas/999999")
    assert r.status_code == 404
