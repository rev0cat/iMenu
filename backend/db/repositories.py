"""
Repository functions for database CRUD operations.
"""
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from db.entities import User, RecipeSession, DiscussionEventRecord, FollowUpRecord
from models import (
    CookingRequest,
    FullRecipe,
    DiscussionEvent,
    FollowUpResponse,
    SessionSummary,
    FollowUpSummary,
)


# ================== User Repository ==================

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return session.get(User, user_id)


def create_user(session: Session, email: str, password_hash: str) -> User:
    """Create a new user."""
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ================== Recipe Session Repository ==================

def create_recipe_session(
    session: Session,
    user_id: int,
    request: CookingRequest,
    full_recipe: FullRecipe,
    rounds_used: int
) -> RecipeSession:
    """Create a new recipe session."""
    recipe_session = RecipeSession(
        user_id=user_id,
        request_json=request.model_dump(),
        result_json=full_recipe.model_dump(),
        rounds_used=rounds_used
    )
    session.add(recipe_session)
    session.commit()
    session.refresh(recipe_session)
    return recipe_session


def list_sessions_by_user(
    session: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0
) -> List[SessionSummary]:
    """List recipe sessions for a user."""
    statement = (
        select(RecipeSession)
        .where(RecipeSession.user_id == user_id)
        .order_by(RecipeSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    results = session.exec(statement).all()
    
    summaries = []
    for rs in results:
        result_json = rs.result_json or {}
        dish = result_json.get("dish", {})
        constraints = result_json.get("constraints", {})
        
        summaries.append(SessionSummary(
            id=rs.id,
            created_at=rs.created_at,
            dish_name=dish.get("name"),
            goal=constraints.get("goal"),
            rounds_used=rs.rounds_used
        ))
    
    return summaries


def get_session_by_id(
    session: Session,
    user_id: int,
    session_id: int
) -> Optional[RecipeSession]:
    """Get a recipe session by ID, verifying user ownership."""
    statement = select(RecipeSession).where(
        RecipeSession.id == session_id,
        RecipeSession.user_id == user_id
    )
    return session.exec(statement).first()


# ================== Discussion Event Repository ==================

def save_discussion_events(
    session: Session,
    session_id: int,
    events: List[DiscussionEvent]
) -> None:
    """Save discussion events for a session."""
    for event in events:
        record = DiscussionEventRecord(
            session_id=session_id,
            event_json=event.model_dump()
        )
        session.add(record)
    session.commit()


def get_discussion_events(
    session: Session,
    session_id: int
) -> List[DiscussionEventRecord]:
    """Get discussion events for a session."""
    statement = (
        select(DiscussionEventRecord)
        .where(DiscussionEventRecord.session_id == session_id)
        .order_by(DiscussionEventRecord.created_at)
    )
    return list(session.exec(statement).all())


# ================== Follow-up Repository ==================

def append_followup_record(
    session: Session,
    session_id: int,
    question: str,
    response: FollowUpResponse
) -> FollowUpRecord:
    """Append a follow-up record to a session."""
    record = FollowUpRecord(
        session_id=session_id,
        question=question,
        answer_json=response.model_dump()
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_followups(
    session: Session,
    session_id: int
) -> List[FollowUpSummary]:
    """List follow-ups for a session."""
    statement = (
        select(FollowUpRecord)
        .where(FollowUpRecord.session_id == session_id)
        .order_by(FollowUpRecord.created_at)
    )
    results = session.exec(statement).all()
    
    return [
        FollowUpSummary(
            id=record.id,
            created_at=record.created_at,
            question=record.question
        )
        for record in results
    ]


def get_followup_by_id(
    session: Session,
    followup_id: int
) -> Optional[FollowUpRecord]:
    """Get a follow-up record by ID."""
    return session.get(FollowUpRecord, followup_id)
