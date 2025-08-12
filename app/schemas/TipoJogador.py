from sqlmodel import Field, SQLModel
from typing import Optional
from app.models import TipoJogadorBase


class TipoJogadorPublico(TipoJogadorBase):
    id: int