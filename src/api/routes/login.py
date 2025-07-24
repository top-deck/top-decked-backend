from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.security import Token, autenticar, criar_token_de_acesso, ACCESS_TOKEN_EXPIRE_MINUTES

from typing import Annotated

from src.services.UsuarioService import retornar_info_por_usuario
from src.core.db import SessionDep


router = APIRouter(tags=["Login"])

@router.post("/login/token")
async def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
    ) -> Token:
    usuario = autenticar(formulario.username, formulario.password, session)
    if not usuario:
        raise HTTPException(
            status_code=usuario.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    dados = retornar_info_por_usuario(usuario, session)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_de_acesso(
        dados=dados, delta_expiracao=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

