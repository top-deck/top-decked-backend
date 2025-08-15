from sqlmodel import Field
from app.models import JogadorBase
from pydantic import BaseModel
from typing import List
from app.utils.Enums import MesEnum
from app.schemas.Torneio import TorneioJogadorPublico


class JogadorPublico(JogadorBase):
    id: int
    pokemon_id: str | None

class JogadorPublicoLoja(JogadorBase):
    id: int
    pokemon_id: str | None
    tipo_jogador_id: int | None

class JogadorUpdate(JogadorBase):
    nome: str | None = None
    senha: str | None = None
    pokemon_id: str | None = None

class JogadorCriar(JogadorBase):
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)
    

class EstatisticasAnuais(BaseModel):
    mes: MesEnum
    ano: int
    pontos: float
    vitorias: int
    derrotas: int
    empates: int


class JogadorEstatisticas(BaseModel):
    torneio_totais: int
    taxa_vitoria: int = 0
    rank_geral: int
    rank_mensal: int
    rank_anual: int
    estatisticas_anuais: List["EstatisticasAnuais"]
    historico: List["TorneioJogadorPublico"]