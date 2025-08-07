from typing import Optional
from sqlmodel import SQLModel, Field
from passlib.hash import bcrypt

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    tipo: str = Field(index=True)
    senha: str = Field(index=True)

    def set_senha(self, senha_clara: str):
        self.senha = bcrypt.hash(senha_clara)