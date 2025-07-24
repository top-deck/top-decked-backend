from models.Usuario import Usuario, UsuarioCriar
from sqlmodel import Field,SQLModel, Relationship

class JogadorBase(SQLModel):
    name: str

class Jogador(JogadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})

class JogadorPublico(JogadorBase):
    id: int
    
class JogadorUpdate(JogadorBase):
    name: str | None = None
    senha: str | None = None

class JogadorCriar(JogadorBase):
    usuario: UsuarioCriar | None = Field(default=None) 