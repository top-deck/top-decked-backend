from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.security import Token, autenticar, criar_token_de_acesso, ACCESS_TOKEN_EXPIRE_MINUTES

from typing import Annotated


router = APIRouter(tags=["Login"])


@router.post("/token")
async def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    usuario = autenticar(formulario.username, formulario.password)
    if not usuario:
        raise HTTPException(
            status_code=usuario.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_de_acesso(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

