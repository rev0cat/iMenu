"""
Database entities using SQLModel.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from sqlalchemy import Text


class User(SQLModel, table=True):
    """User entity for authentication."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    sessions: List["RecipeSession"] = Relationship(back_populates="user")


class RecipeSession(SQLModel, table=True):
    """Recipe session entity storing each recipe generation."""
    __tablename__ = "recipe_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request_json: dict = Field(default={}, sa_column=Column(JSON))
    result_json: dict = Field(default={}, sa_column=Column(JSON))
    rounds_used: int = Field(default=1)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="sessions")
    discussion_events: List["DiscussionEventRecord"] = Relationship(back_populates="session")
    followups: List["FollowUpRecord"] = Relationship(back_populates="session")


class DiscussionEventRecord(SQLModel, table=True):
    """Record of discussion events for replay."""
    __tablename__ = "discussion_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="recipe_sessions.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_json: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    session: Optional[RecipeSession] = Relationship(back_populates="discussion_events")


class FollowUpRecord(SQLModel, table=True):
    """Record of follow-up questions and answers."""
    __tablename__ = "followup_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="recipe_sessions.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    question: str = Field(sa_column=Column(Text))
    answer_json: dict = Field(default={}, sa_column=Column(JSON))
    
    # Relationships
    session: Optional[RecipeSession] = Relationship(back_populates="followups")
