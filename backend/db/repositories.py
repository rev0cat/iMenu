from typing import List, Optional
from sqlmodel import select
from .session import get_session
from .entities import RecipeSession, User, DiscussionEventRecord, FollowUpRecord
from backend.models import CookingRequest, FullRecipe, DiscussionEvent, FollowUpResponse


def create_user(email: str, password_hash: str) -> User:
    with get_session() as session:
        user = User(email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user_by_email(email: str) -> Optional[User]:
    with get_session() as session:
        result = session.exec(select(User).where(User.email == email)).first()
        return result


def get_user(user_id: int) -> Optional[User]:
    with get_session() as session:
        return session.get(User, user_id)


def create_session(user_id: int, request: CookingRequest, full_recipe: FullRecipe, rounds_used: int) -> RecipeSession:
    with get_session() as session:
        record = RecipeSession(
            user_id=user_id,
            request_json=request.dict(),
            result_json=full_recipe.dict(),
            rounds_used=rounds_used,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def list_sessions_by_user(user_id: int, limit: int = 20, offset: int = 0) -> List[RecipeSession]:
    with get_session() as session:
        stmt = select(RecipeSession).where(RecipeSession.user_id == user_id).offset(offset).limit(limit)
        return list(session.exec(stmt).all())


def get_session_by_id(user_id: int, session_id: int) -> Optional[RecipeSession]:
    with get_session() as session:
        stmt = select(RecipeSession).where(
            RecipeSession.user_id == user_id, RecipeSession.id == session_id
        )
        return session.exec(stmt).first()


def save_discussion_events(session_id: int, events: List[DiscussionEvent]) -> None:
    if not events:
        return
    with get_session() as session:
        for event in events:
            record = DiscussionEventRecord(session_id=session_id, event_json=event.dict())
            session.add(record)
        session.commit()


def append_followup_record(session_id: int, question: str, response: FollowUpResponse) -> FollowUpRecord:
    with get_session() as session:
        record = FollowUpRecord(session_id=session_id, question=question, answer_json=response.dict())
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def list_followups(session_id: int) -> List[FollowUpRecord]:
    with get_session() as session:
        stmt = select(FollowUpRecord).where(FollowUpRecord.session_id == session_id)
        return list(session.exec(stmt).all())

