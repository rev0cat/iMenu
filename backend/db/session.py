from contextlib import contextmanager
from sqlmodel import Session
from .base import engine


@contextmanager
def get_session() -> Session:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

