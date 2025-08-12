from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date
from passlib.hash import bcrypt


# ---------------------------------- Usuario ----------------------------------
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    tipo: str = Field(index=True)
    senha: str = Field(index=True)

    def set_senha(self, senha_clara: str):
        self.senha = bcrypt.hash(senha_clara)


# ---------------------------------- Jogador ----------------------------------
class JogadorBase(SQLModel):
    nome: str


class Jogador(JogadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=True)
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    pokemon_id: str | None = Field(default=None, nullable=True, unique=True)
    torneios: List["JogadorTorneioLink"] = Relationship(
        back_populates="jogador")


# ---------------------------------- JogadorTorneioLink ----------------------------------
class JogadorTorneioLinkBase(SQLModel):
    tipo_jogador_id: int | None = Field(
        default=None, foreign_key="tipojogador.id")


class JogadorTorneioLink(JogadorTorneioLinkBase, table=True):
    jogador_id: str | None = Field(
        default=None, foreign_key="jogador.pokemon_id", primary_key=True)
    torneio_id: str | None = Field(
        default=None, foreign_key="torneio.id", primary_key=True, ondelete="CASCADE")
    jogador: Optional["Jogador"] | None = Relationship(back_populates="torneios")


# ---------------------------------- Loja ----------------------------------
class LojaBase(SQLModel):
    nome: str = Field(index=True)
    endereco: str = Field(default=None, index=True)


class Loja(LojaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", unique=True)
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})


# ---------------------------------- Rodada ----------------------------------
class Rodada(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    jogador1_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    jogador2_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    torneio_id: str = Field(default=None, foreign_key="torneio.id")
    vencedor: str = Field(
        default=None, foreign_key="jogador.pokemon_id", nullable=True)
    num_rodada: int = Field(default=None)
    mesa: Optional[int] = Field(default=None)
    data_de_inicio: date = Field(default=None)


# ---------------------------------- TipoJogador ----------------------------------
class TipoJogadorBase(SQLModel):
    nome: str = Field(default=None)
    pt_vitoria: int = Field(default=None)
    pt_derrota: int = Field(default=None)
    pt_oponente_perde: int = Field(default=None)
    pt_oponente_ganha: int = Field(default=None)
    tcg: str = Field(default=None)


class TipoJogador(TipoJogadorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loja: int | None = Field(default=None, foreign_key="loja.id")
    

# ---------------------------------- Torneio ----------------------------------
class TorneioBase(SQLModel):
    nome: str = Field(default=None)
    descricao: str = Field(default=None)
    cidade: str = Field(index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: bool = Field(default=False)


class Torneio(TorneioBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    loja: Optional[Loja] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    jogadores: List["JogadorTorneioLink"] = Relationship()