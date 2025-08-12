from typing import Optional, List, Dict
from app.schemas.JogadorTorneioLink import JogadorTorneioLinkPublico
from app.models import TorneioBase
from datetime import date


class TorneioAtualizar(TorneioBase):
    nome: str | None = None
    descricao: str | None = None
    cidade: str | None = None
    estado: str | None = None
    tempo_por_rodada: int | None = None
    data_inicio: date | None = None
    finalizado: bool | None = None
    regra_basica: int | None = None
    regras_adicionais: Optional[Dict[str, int]] | None = None


class TorneioPublico(TorneioBase):
    id: str
    jogadores: List["JogadorTorneioLinkPublico"]