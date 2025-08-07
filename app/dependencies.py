from app.core.security import (
    OAUTH2_SCHEME, 
    ALGORITHM, 
    SECRET_KEY, 
    TokenData, validar_token)
from app.core.exception import EXCEPTIONS

from typing import Annotated
from fastapi import Depends
import jwt


async def retornar_usuario_atual(token: Annotated[str, Depends(OAUTH2_SCHEME)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if not validar_token(payload=payload):
        raise EXCEPTIONS.unauthorized()

    id = payload.get("id")
    tipo = payload.get("tipo")
    nome = payload.get("nome")
    email = payload.get("email")
    usuario_id = payload.get("usuario_id")

    token_data = TokenData(id=id, tipo=tipo, nome=nome,
                           email=email, usuario_id=usuario_id)

    if tipo == "loja":
        token_data.endereco = payload.get("endereco")

    return token_data


async def retornar_loja_atual(token_data: Annotated[str, Depends(retornar_usuario_atual)]):
    if not token_data.tipo == "loja":
        raise EXCEPTIONS.forbidden()

    return token_data