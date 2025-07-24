from src.core.db import SessionDep
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from src.models.Usuario import Usuario
from src.models.Jogador import Jogador
from src.models.Loja import Loja
from sqlmodel import select
from sqlalchemy import func
from src.core.security import oauth2_scheme

def verificar_novo_usuario(email: str, session: SessionDep) -> str:
    try:
        valid = validate_email(email)
        num_usuarios = session.scalar(select(func.count(Usuario.id)).where(Usuario.email == email))

        if num_usuarios > 0:
            raise HTTPException(status_code=400, detail=f"e-mail já cadastrado: {email}")
        
        return valid.email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail=f"e-mail inválido: {email}")


def retornar_info_por_usuario(usuario: Usuario, session: SessionDep) -> dict:
    infos = {}
    linha_db_info = {}
    
    if usuario.tipo == "jogador":
        linha_db_info = session.exec(select(Jogador).where(Jogador.usuario_id == usuario.id)).first()
    else:
        linha_db_info = session.exec(select(Loja).where(Loja.usuario_id == usuario.id)).first()
        infos["endereco"] = linha_db_info.endereco
        infos["email"] = usuario.email

    infos["nome"] = linha_db_info.nome
    infos["usuario_id"] = linha_db_info.usuario_id
    infos["email"] = usuario.email
        
    return infos