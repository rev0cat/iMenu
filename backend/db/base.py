from sqlmodel import SQLModel, create_engine
from backend.config import settings

engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    from backend.db import entities  # noqa: F401

    SQLModel.metadata.create_all(engine)
