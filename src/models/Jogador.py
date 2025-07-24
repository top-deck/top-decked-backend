from src.models.Usuario import Usuario
from sqlmodel import Field,SQLModel, Relationship

class JogadorBase(SQLModel):
    nome: str

class Jogador(JogadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", unique=True)
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})

class JogadorPublico(JogadorBase):
    id: int
    
class JogadorUpdate(JogadorBase):
    nome: str | None = None
    senha: str | None = None

class JogadorCriar(JogadorBase):
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)