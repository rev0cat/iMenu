from sqlmodel import SQLModel, create_engine
from backend.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    from . import entities  # noqa: F401

    SQLModel.metadata.create_all(engine)

