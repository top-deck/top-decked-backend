from sqlmodel import Field, SQLModel
from datetime import date, datetime
from typing import Optional

class Rodada(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    jogador1_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    jogador2_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    torneio_id: str = Field(default=None, foreign_key="torneio.id")
    vencedor: str = Field(default=None, foreign_key="jogador.pokemon_id")
    num_rodada: int = Field(default=None)
    mesa: Optional[int] = Field(default=None)
    data_de_inicio: date = Field(default=datetime.now)
