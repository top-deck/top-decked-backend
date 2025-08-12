from typing import Optional
from app.models import JogadorTorneioLinkBase


class JogadorTorneioLinkPublico(JogadorTorneioLinkBase):
    jogador_id: str
    nome: Optional[str]
    tipo_jogador_id: Optional[int]