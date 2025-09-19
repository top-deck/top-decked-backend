from typing import Optional
from app.models import JogadorTorneioLinkBase


class JogadorTorneioLinkPublico(JogadorTorneioLinkBase):
    nome: Optional[str]
    colocacao: Optional[int]
    usuario_id: Optional[int]