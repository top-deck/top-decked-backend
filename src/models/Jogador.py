from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class JogadorBase(SQLModel):
    name: str
    email: str = Field(default=None, index=True)

class Jogador(JogadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    senha : str

class JogadorPublico(JogadorBase):
    id: int
    
class JogadorUpdate(JogadorBase):
    name: str | None = None
    email: str | None = None
    senha: str | None = None

class JogadorCriar(JogadorBase):
    senha: str