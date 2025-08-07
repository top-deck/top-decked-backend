from app.core.db import SessionDep
from email_validator import validate_email, EmailNotValidError
from core.exception import EXCEPTIONS
from app.models.Usuario import Usuario
from app.models.Jogador import Jogador
from app.models.Loja import Loja
from sqlmodel import select
from sqlalchemy import func
from app.core.security import OAUTH2_SCHEME

def verificar_novo_usuario(email: str, session: SessionDep) -> str:
    try:
        valid = validate_email(email)
        num_usuarios = session.scalar(select(func.count(Usuario.id)).where(Usuario.email == email))

        if num_usuarios > 0:
            raise EXCEPTIONS.bad_request("e-mail já cadastrado: '{email}'")
        
        return valid.normalized
    except EmailNotValidError:
        raise EXCEPTIONS.bad_request("e-mail inválido: '{email}'")


def retornar_info_por_usuario(usuario: Usuario, session: SessionDep) -> dict:
    infos = {}
    linha_db_info = {}
    
    if usuario.tipo == "jogador":
        linha_db_info = session.exec(select(Jogador).where(Jogador.usuario_id == usuario.id)).first()
    else:
        linha_db_info = session.exec(select(Loja).where(Loja.usuario_id == usuario.id)).first()
        infos["endereco"] = linha_db_info.endereco
        
    infos["id"] = linha_db_info.id
    infos["nome"] = linha_db_info.nome
    infos["usuario_id"] = linha_db_info.usuario_id
    infos["email"] = usuario.email
    infos["tipo"] = usuario.tipo
   
    return infos