from pydantic import BaseModel

class Ranking(BaseModel):
    nome_jogador: str
    pontos: float
    torneios: int
    vitorias: int
    derrotas: int
    empates: int
    taxa_vitoria: float

class RankingPorLoja(BaseModel):
    nome_jogador: str
    nome_loja: str
    pontos: float
    torneios: int
    vitorias: int
    derrotas: int
    empates: int
    taxa_vitoria: float