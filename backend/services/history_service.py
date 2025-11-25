from typing import List
from backend import models
from backend.db import repositories
from backend.db.session import session_scope


def list_user_sessions(user_id: int, limit: int = 20, offset: int = 0):
    with session_scope() as session:
        sessions = repositories.list_sessions_by_user(session, user_id, limit, offset)
        return sessions


def get_session_detail(user_id: int, session_id: int):
    with session_scope() as session:
        record = repositories.get_session_by_id(session, user_id, session_id)
        if not record:
            return None
        followups = repositories.list_followups(session, session_id)
        return record, followups
