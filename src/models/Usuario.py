from typing import Optional
from sqlmodel import SQLModel, Field
from passlib.hash import bcrypt

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    senha: str

    def set_senha(self, senha_clara: str):
        self.senha = bcrypt.hash(senha_clara)


class UsuarioCriar(SQLModel):
    email: str
    senha: str
