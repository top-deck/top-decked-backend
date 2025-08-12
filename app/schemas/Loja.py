from sqlmodel import Field
from app.models import LojaBase


class LojaPublico(LojaBase):
    id: int


class LojaCriar(LojaBase):
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)


class LojaAtualizar(LojaBase):
    nome: str | None = None
    endereco: str | None = None
    email: str | None = None
    senha: str | None = None