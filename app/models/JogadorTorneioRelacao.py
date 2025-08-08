from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class JogadorTorneioRelacao(SQLModel, table=True):
    jogador_id: str | None = Field(
        default=None, foreign_key="jogador.pokemon_id", primary_key=True)
    torneio_id: str | None = Field(
        default=None, foreign_key="torneio.id", primary_key=True)
    tipo_jogador_id: int | None = Field(
        default=None, foreign_key="tipojogador.id")