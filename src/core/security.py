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

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verificar_senha(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def retornar_senha_criptografada(password):
    return pwd_context.hash(password)


def retornar_usuario_pelo_email(*, sessao: Session, email: str) -> Usuario | None:
    consulta = select(Usuario).where(Usuario.email == email)
    usuario_atual = sessao.exec(consulta).first()
    return usuario_atual
    

def autenticar(*, session: Session, email: str, password: str) -> Usuario | None:
    db_user = retornar_usuario_pelo_email(session=session, email=email)
    if not db_user:
        return None
    if not verificar_senha(password, db_user.hashed_password):
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


# async def retornar_usuario_atual(token: Annotated[str, Depends(oauth2_scheme)]):
#     credenciais_excecao = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise credenciais_excecao
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credenciais_excecao
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credenciais_excecao
#     return user


# async def retornar_usuario_atual_ativo(
#     current_user: Annotated[Usuario, Depends(retornar_usuario_atual)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user