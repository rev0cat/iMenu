from typing import List, Optional
from sqlmodel import Session, select
from backend import models
from backend.db import entities


def create_user(session: Session, email: str, password_hash: str) -> entities.User:
    user = entities.User(email=email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str) -> Optional[entities.User]:
    statement = select(entities.User).where(entities.User.email == email)
    return session.exec(statement).first()


def create_session(
    session: Session, user_id: int, request: models.CookingRequest, full_recipe: models.FullRecipe
) -> entities.RecipeSession:
    record = entities.RecipeSession(
        user_id=user_id,
        request_json=request.dict(),
        result_json=full_recipe.dict(),
        rounds_used=full_recipe.review_rounds_used,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_sessions_by_user(session: Session, user_id: int, limit: int = 20, offset: int = 0) -> List[entities.RecipeSession]:
    statement = (
        select(entities.RecipeSession)
        .where(entities.RecipeSession.user_id == user_id)
        .order_by(entities.RecipeSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_session_by_id(session: Session, user_id: int, session_id: int) -> Optional[entities.RecipeSession]:
    statement = select(entities.RecipeSession).where(
        entities.RecipeSession.id == session_id, entities.RecipeSession.user_id == user_id
    )
    return session.exec(statement).first()


def save_discussion_events(
    session: Session, session_id: int, events: List[models.DiscussionEvent]
) -> List[entities.DiscussionEventRecord]:
    records = [
        entities.DiscussionEventRecord(session_id=session_id, event_json=event.dict()) for event in events
    ]
    session.add_all(records)
    session.commit()
    for record in records:
        session.refresh(record)
    return records


def append_followup_record(
    session: Session, session_id: int, question: str, response: models.FollowUpResponse
) -> entities.FollowUpRecord:
    record = entities.FollowUpRecord(session_id=session_id, question=question, answer_json=response.dict())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_followups(session: Session, session_id: int) -> List[entities.FollowUpRecord]:
    statement = (
        select(entities.FollowUpRecord)
        .where(entities.FollowUpRecord.session_id == session_id)
        .order_by(entities.FollowUpRecord.created_at.desc())
    )
    return list(session.exec(statement).all())
