from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date

class Torneio(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    cidade: str = Field(index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: bool = Field(default=False)