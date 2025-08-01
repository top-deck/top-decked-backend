from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from sqlmodel import Session, select

from src.models.Usuario import Usuario
from src.core.db import SessionDep, get_session
from fastapi.security import OAuth2PasswordBearer


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id : int | None = None
    tipo: str | None = None
    nome: str | None = None
    email: str | None = None
    usuario_id: int | None = None
    endereco: str | None = None


def verificar_senha(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def retornar_senha_criptografada(password):
    return pwd_context.hash(password)


def retornar_usuario_pelo_email(email: str, session: SessionDep) -> Usuario | None:
    consulta = select(Usuario).where(Usuario.email == email)
    usuario_atual = session.exec(consulta).first()
    return usuario_atual
    

def autenticar(email: str, forms_senha: str, session: SessionDep) -> Usuario | None:
    db_user = retornar_usuario_pelo_email(session=session, email=email)
    if not db_user:
        return None
    if not verificar_senha(forms_senha, db_user.senha):
        return None
    return db_user


def criar_token_de_acesso(dados: dict, delta_expiracao: timedelta | None = None):
    criptografar = dados.copy()
    if delta_expiracao:
        expiracao = datetime.now(timezone.utc) + delta_expiracao
    else:
        expiracao = datetime.now(timezone.utc) + timedelta(minutes=15)
    criptografar.update({"exp": expiracao})
    encoded_jwt = jwt.encode(criptografar, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def _validar_token(payload) -> bool:
    try:
        email = payload.get("email")
        if email is None:
            return False
    except InvalidTokenError:
        return False
    
    session = get_session()
    usuario = session.exec(select(Usuario).where(
        Usuario.email == email)).first()
    if usuario is None:
        return False
    return True
    
async def retornar_usuario_atual(token: Annotated[str, Depends(oauth2_scheme)]):
    credenciais_excecao = HTTPException(
        status_code=401,
        detail="Autenticação negada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(payload)
    if not _validar_token(payload=payload):
        raise credenciais_excecao
    
    id = payload.get("id")
    tipo = payload.get("tipo")
    nome = payload.get("nome")
    email = payload.get("email")
    usuario_id = payload.get("usuario_id")
    
    token_data = TokenData(id=id, tipo=tipo, nome=nome, email=email, usuario_id=usuario_id)
    
    if tipo == "loja":
        token_data.endereco = payload.get("endereco")

    return token_data