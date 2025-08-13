from typing import Optional, List, Dict
from app.schemas.JogadorTorneioLink import JogadorTorneioLinkPublico
from app.models import TorneioBase, RodadaBase
from datetime import date, time


class TorneioAtualizar(TorneioBase):
    nome: str | None = None
    descricao: str | None = None
    cidade: str | None = None
    estado: str | None = None
    tempo_por_rodada: int | None = None
    data_inicio: date | None = None
    finalizado: bool | None = None
    vagas: int | None = None
    hora: time | None = None
    formato: str | None = None
    taxa: float | None = None
    premio: str | None = None
    n_rodadadas: int | None = None
    pontuacao_de_participacao: int | None = None
    
    regra_basica_id: int | None = None
    regras_adicionais: Optional[Dict[str, int]] | None = None


class TorneioPublico(TorneioBase):
    id: str
    jogadores: List["JogadorTorneioLinkPublico"] | None
    rodadas: List["RodadaBase"] | None