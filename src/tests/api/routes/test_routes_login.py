from fastapi.testclient import TestClient
from src.tests.db.config import app 

client = TestClient(app)

def test_login_token_sucesso():
    payload_cadastro = {
        "nome": "Teste Login",
        "email": "teste.login@gmail.com",
        "senha": "minhasenha"
    }
    client.post("/jogadores/", json=payload_cadastro)

    login_data = {
        "username": "teste.login@gmail.com", 
        "password": "minhasenha"
    }
    response = client.post("/login/token", data=login_data)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_token_senha_errada():
    payload_cadastro = {
        "nome": "Teste Login Fail",
        "email": "teste.fail@gmail.com",
        "senha": "senha_correta"
    }
    client.post("/jogadores/", json=payload_cadastro)

    login_data = {
        "username": "teste.fail@gmail.com",
        "password": "senha_errada"
    }
    response = client.post("/login/token", data=login_data)
    assert response.status_code == 401
    assert "detail" in response.json()

def test_login_token_usuario_inexistente():
    login_data = {
        "username": "nao.existe@example.com",
        "password": "qualquer"
    }
    response = client.post("/login/token", data=login_data)
    assert response.status_code == 401
    assert "detail" in response.json()
