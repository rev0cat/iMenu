from contextlib import contextmanager
from sqlmodel import Session
from backend.db.base import engine


def get_session() -> Session:
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope():
    with Session(engine) as session:
        yield session
