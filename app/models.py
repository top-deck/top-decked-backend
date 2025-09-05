from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, time
import uuid
from app.core.db import SessionDep
from email_validator import validate_email, EmailNotValidError
from app.core.exception import TopDeckedException
from sqlmodel import select
from sqlalchemy import func
from passlib.context import CryptContext


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
# ---------------------------------- Usuario ----------------------------------
class UsuarioBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    foto: Optional[str] = Field(default=None, unique=True)


class Usuario(UsuarioBase, table=True):
    tipo: str = Field(index=True)
    senha: str = Field(index=True)

    def set_senha(self, senha_clara: str):
        self.senha = PWD_CONTEXT.hash(senha_clara)

    def set_email(self, email : str, session: SessionDep):
        try:
            # Olhar o que é esse va;od
            valid = validate_email(email)
            num_usuarios = session.scalar(select(func.count(Usuario.id)).where(Usuario.email == email))

            if num_usuarios > 0:
                raise TopDeckedException.bad_request(f"email cadastrado: '{email}'")
            
            self.email = email
        except EmailNotValidError:
            raise TopDeckedException.bad_request(f"e-mail inválido: '{email}'")

# ---------------------------------- Jogador ----------------------------------
class JogadorBase(SQLModel):
    nome: str
    telefone: str = Field(default=None, max_length=11)
    data_nascimento: date = Field(default=None)


class Jogador(JogadorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=True, ondelete="SET NULL")
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
    torneio: Optional["Torneio"] | None = Relationship(back_populates="jogadores")
    tipo_jogador: Optional["TipoJogador"] | None = Relationship()
    jogador: Optional["Jogador"] | None = Relationship(back_populates="torneios")


# ---------------------------------- Loja ----------------------------------
class LojaBase(SQLModel):
    nome: str = Field(index=True)
    endereco: str = Field(default=None, index=True)
    telefone: str = Field(default=None, nullable=True)
    site: str = Field(default=None)


class Loja(LojaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", unique=True)
    usuario: Usuario = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    torneios: List["Torneio"] = Relationship(back_populates="loja")


# ---------------------------------- Rodada ----------------------------------
class RodadaBase(SQLModel):
    jogador1_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    jogador2_id: str = Field(default=None, foreign_key="jogador.pokemon_id")
    vencedor: Optional[str] = Field(
        default=None, foreign_key="jogador.pokemon_id", nullable=True)
    num_rodada: int = Field(default=None)
    mesa: Optional[int] = Field(default=None)
    data_de_inicio: date = Field(default=None)

class Rodada(RodadaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    torneio_id: str = Field(default=None, foreign_key="torneio.id", ondelete="CASCADE")


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
    cidade: Optional[str] = Field(default=None, index=True, nullable=True)
    estado: Optional[str] = Field(default=None, index=True, nullable=True)
    tempo_por_rodada: int = Field(default=30, index=True)
    data_inicio: date = Field(default=None)
    finalizado: Optional[bool] = Field(default=False)
    vagas: int = Field(default=0)
    hora: Optional[time] = Field(default=None, nullable=True)
    formato: Optional[str] = Field(default="Desconhecido", nullable=True)
    taxa: float = Field(default=0)
    premio: Optional[str] = Field(default=None, nullable=True)
    n_rodadadas: int = Field(default=0)
    regra_basica_id: Optional[int] = Field(
        default=None, foreign_key="tipojogador.id", nullable=True)
    pontuacao_de_participacao: int = Field(default=0)


class Torneio(TorneioBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    loja_id: int = Field(foreign_key="loja.id", nullable=True)
    loja: Optional["Loja"] = Relationship(back_populates="torneios", sa_relationship_kwargs={"lazy": "joined"})
    rodadas: List["Rodada"] = Relationship(sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    jogadores: List["JogadorTorneioLink"] = Relationship(back_populates="torneio", 
                                                         sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    regra_basica: Optional["TipoJogador"] = Relationship()