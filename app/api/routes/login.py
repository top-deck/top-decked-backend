from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import Token, autenticar, criar_token_de_acesso, ACCESS_TOKEN_EXPIRE_MINUTES, TokenData
from app.dependencies import retornar_usuario_atual

from typing import Annotated

from app.services.UsuarioService import retornar_info_por_usuario
from app.core.db import SessionDep
from app.models.Usuario import Usuario

router = APIRouter(
    prefix="/login",
    tags=["Login"])

@router.post("/token")
async def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
    ) -> Token:
    usuario = autenticar(formulario.username, formulario.password, session)

    dados = retornar_info_por_usuario(usuario, session)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_de_acesso(
        dados=dados, delta_expiracao=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/profile")
async def ler_token(
        dados_token: Annotated[TokenData, Depends(retornar_usuario_atual)]):
    return dados_token
