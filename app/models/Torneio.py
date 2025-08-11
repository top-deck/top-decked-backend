from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date
from app.models.Loja import Loja
from app.models.Jogador import JogadorPublicoLoja
from datetime import time
import uuid

class TorneioBase(SQLModel):
    nome: str = Field(default=None)
    descricao: str = Field(default=None)
    cidade: Optional[str] = Field(default=None, index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: Optional[bool] = Field(default=False)
    vagas: int = Field(default=0)
    hora : Optional[time] = Field(default=None)
    formato: str = Field(default=None)
    taxa: float = Field(default=0)
    premio: Optional[str] = Field(default=None)
    n_rodadadas: int = Field(default=0)

class Torneio(TorneioBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    loja: Optional[Loja] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    

class TorneioPublico(TorneioBase):
    jogadores: list["JogadorPublicoLoja"] = Field(default = [])