from sqlalchemy import create_engine
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine

from src.core.db import get_session
from src.main import app

current_file_path = Path(__file__).resolve()

db_path = "test.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


def override_get_session():
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
app.dependency_overrides[get_session] = override_get_session
