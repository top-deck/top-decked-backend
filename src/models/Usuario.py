from sqlmodel import Field, SQLModel


class UsuarioBase(SQLModel):
    email: str = Field(index=True)
    tipo: str = Field(default=None, index=True)


class Usuario(UsuarioBase):
    senha: str
    

class UsuarioPublico(UsuarioBase):
    pass