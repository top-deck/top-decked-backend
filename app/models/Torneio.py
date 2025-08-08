from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, Dict
from datetime import date
from app.models.Loja import Loja
from app.models.TipoJogador import TipoJogador
from app.models.Jogador import JogadorPublicoLoja

class TorneioBase(SQLModel):
    nome: str = Field(default=None)
    descricao: str = Field(default=None)
    cidade: str = Field(index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: bool = Field(default=False)
    

class Torneio(TorneioBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    loja: Optional[Loja] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    

class TorneioAtualizar(TorneioBase):
    regra_basica: int
    regras_adicionais: Optional[Dict[str, int]]

class TorneioPublico(TorneioBase):
    id: str
    jogadores: list["JogadorPublicoLoja"]
