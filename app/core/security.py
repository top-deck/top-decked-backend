from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from sqlmodel import select

from app.models.Usuario import Usuario
from app.core.db import SessionDep, get_session
from app.core.exception import TopDeckedException
from fastapi.security import OAuth2PasswordBearer

import os

SECRET_KEY = os.getenv("SECURITY_SECRET_KEY")
ALGORITHM = os.getenv("SECURITY_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SECURITY_TOKEN_EXPIRATION"))

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login/token")
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def retornar_senha_criptografada(password):
    return PWD_CONTEXT.hash(password)


def retornar_usuario_pelo_email(email: str, session: SessionDep) -> Usuario | None:
    consulta = select(Usuario).where(Usuario.email == email)
    usuario_atual = session.exec(consulta).first()
    return usuario_atual
    

def autenticar(email: str, forms_senha: str, session: SessionDep) -> Usuario | None:
    db_user = retornar_usuario_pelo_email(session=session, email=email)
    if not db_user or not verificar_senha(forms_senha, db_user.senha):
        raise TopDeckedException.unauthorized()
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

async def validar_token(payload) -> bool:
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