from sqlmodel import Field
from app.models import JogadorBase
    
    
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