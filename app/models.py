from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, time
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
    jogador_id: str | None = Field(
        default=None, foreign_key="jogador.pokemon_id", primary_key=True)
    tipo_jogador_id: int | None = Field(
        default=None, foreign_key="tipojogador.id")
    pontuacao: float = Field(default=0)
    pontuacao_com_regras: float = Field(default=0)

class JogadorTorneioLink(JogadorTorneioLinkBase, table=True):
    torneio_id: str | None = Field(
        default=None, foreign_key="torneio.id", primary_key=True, ondelete="CASCADE")
    tipo_jogador: Optional["TipoJogador"] | None = Relationship()
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
class RodadaBase(SQLModel):
    jogador1_id: str = Field(primary_key=True,
            default=None, foreign_key="jogador.pokemon_id")
    jogador2_id: str = Field(
        primary_key=True, default=None, foreign_key="jogador.pokemon_id")
    vencedor: Optional[str] = Field(
        default=None, foreign_key="jogador.pokemon_id", nullable=True)
    num_rodada: int = Field(default=None)
    mesa: Optional[int] = Field(default=None)
    data_de_inicio: date = Field(default=None)

class Rodada(RodadaBase, table=True):
    torneio_id: str = Field(
        primary_key=True, default=None, foreign_key="torneio.id")


# ---------------------------------- TipoJogador ----------------------------------
class TipoJogadorBase(SQLModel):
    nome: str = Field(default=None)
    pt_vitoria: float = Field(default=None)
    pt_derrota: float = Field(default=None)
    pt_empate: float = Field(default=None)
    pt_oponente_perde: float = Field(default=None)
    pt_oponente_ganha: float = Field(default=None)
    pt_oponente_empate: float = Field(default=None)
    tcg: str = Field(default=None)


class TipoJogador(TipoJogadorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loja: int | None = Field(default=None, foreign_key="loja.id")
    

# ---------------------------------- Torneio ----------------------------------
class TorneioBase(SQLModel):
    nome: Optional[str] = Field(default=None, nullable=True)
    descricao: Optional[str] = Field(default=None, nullable=True)
    cidade: Optional[str] = Field(default=None, index=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: Optional[bool] = Field(default=False)
    vagas: int = Field(default=0)
    hora: Optional[time] = Field(default=None, nullable=True)
    formato: Optional[str] = Field(default=None, nullable=True)
    taxa: float = Field(default=0)
    premio: Optional[str] = Field(default=None, nullable=True)
    n_rodadadas: int = Field(default=0)
    regra_basica_id: Optional[int] = Field(
        default=None, foreign_key="tipojogador.id", nullable=True)
    pontuacao_de_participacao: int = Field(default=0)


class Torneio(TorneioBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    loja: Optional["Loja"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    rodadas: List["Rodada"] = Relationship()
    jogadores: List["JogadorTorneioLink"] = Relationship()
    regra_basica: Optional["TipoJogador"] = Relationship()