from sqlmodel import Field, SQLModel


class LojaBase(SQLModel):
    nome: str = Field(index=True)
    endereco: str = Field(default=None, index=True)


class Loja(LojaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # senha: 

class LojaPublico(LojaBase):
    id: int


class LojaCriar(LojaBase):
    # senha: str
    pass


class LojaAtualizar(LojaBase):
    nome: str | None = None
    endereco: int | None = None
    # senha: str
