from datetime import datetime
from typing import Optional
from sqlmodel import Column, DateTime, Field, JSON, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecipeSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request_json: dict = Field(sa_column=Column(JSON))
    result_json: dict = Field(sa_column=Column(JSON))
    rounds_used: int


class DiscussionEventRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="recipesession.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_json: dict = Field(sa_column=Column(JSON))


class FollowUpRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="recipesession.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    question: str
    answer_json: dict = Field(sa_column=Column(JSON))
