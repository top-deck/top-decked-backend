from sqlmodel import Field, SQLModel, Relationship
from models.Usuario import UsuarioCriar, Usuario
from typing import Optional


class LojaBase(SQLModel):
    nome: str = Field(index=True)
    endereco: str = Field(default=None, index=True)

class Loja(LojaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})

class LojaPublico(LojaBase):
    id: int


class LojaCriar(LojaBase):
    usuario: UsuarioCriar | None = Field(default=None)


class LojaAtualizar(LojaBase):
    nome: str | None = None
    endereco: str | None = None
    usuario: Usuario | None = None