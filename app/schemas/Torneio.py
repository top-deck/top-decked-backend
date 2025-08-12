from typing import Optional, List, Dict
from app.schemas.JogadorTorneioLink import JogadorTorneioLinkPublico
from app.models import TorneioBase


class TorneioAtualizar(TorneioBase):
    regra_basica: int
    regras_adicionais: Optional[Dict[str, int]]


class TorneioPublico(TorneioBase):
    id: str
    jogadores: List["JogadorTorneioLinkPublico"]