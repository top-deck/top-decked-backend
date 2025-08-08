from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date
from app.models.Loja import Loja
from app.models.Jogador import JogadorPublicoLoja


class TorneioBase(SQLModel):
    id: Optional[str] = Field(default=None, primary_key=True)
    cidade: str = Field(index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: bool = Field(default=False)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    
    
class Torneio(TorneioBase, table=True):
    loja: Optional[Loja] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    

class TorneioPublico(TorneioBase):
    jogadores: list["JogadorPublicoLoja"]