from sqlmodel import Field, SQLModel
from typing import Optional
from app.models import TipoJogadorBase


class TipoJogadorAtualizar(TipoJogadorBase):
    nome: str | None = None
    pt_vitoria: float | None = None
    pt_derrota: float | None = None
    pt_empate: float | None = None
    pt_oponente_perde: float | None = None
    pt_oponente_ganha: float | None = None
    pt_oponente_empate: float | None = None
    tcg: str | None = None

class TipoJogadorPublico(TipoJogadorBase):
    id: int