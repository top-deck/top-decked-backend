from sqlmodel import Field, SQLModel, Relationship
from src.models.Usuario import Usuario, UsuarioPublico
from typing import Optional, List


class LojaBase(SQLModel):
    nome: str = Field(index=True)
    endereco: str = Field(default=None, index=True)
    # usuario: UsuarioPublico = Field(default=None, index=True)

class Loja(LojaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: Usuario | None = Field(default=None)
    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="lojas")
    
class LojaPublico(LojaBase):
    id: int


class LojaCriar(LojaBase):
    usuario: Usuario | None = Field(default=None)


class LojaAtualizar(LojaBase):
    nome: str | None = None
    endereco: int | None = None
    usuario: Usuario | None = None