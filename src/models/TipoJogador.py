from sqlmodel import Field, SQLModel
from typing import Optional


class TipoJogadorBase(SQLModel):
    nome: str = Field(default=None)
    pt_vitoria: int = Field(default=None)
    pt_derrota: int = Field(default=None)
    pt_oponente_perde: int = Field(default=None)
    pt_oponente_ganha: int = Field(default=None)
    tcg: str = Field(default=None)
    
    
class TipoJogador(TipoJogadorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loja: int| None = Field(default=None, foreign_key="loja.id")


class TipoJogadorPublico(TipoJogadorBase):
    id: int