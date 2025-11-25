"""
History service for session management.
"""
from typing import List, Optional
from sqlmodel import Session

from models import (
    CookingRequest,
    FullRecipe,
    SessionSummary,
    SessionDetail,
    FollowUpSummary,
)
from db.repositories import (
    list_sessions_by_user,
    get_session_by_id,
    list_followups,
)


def get_user_history(
    db_session: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0
) -> List[SessionSummary]:
    """
    Get list of recipe sessions for a user.
    
    Args:
        db_session: Database session.
        user_id: User ID.
        limit: Maximum number of results.
        offset: Offset for pagination.
        
    Returns:
        List of session summaries.
    """
    return list_sessions_by_user(db_session, user_id, limit, offset)


def get_session_detail(
    db_session: Session,
    user_id: int,
    session_id: int
) -> Optional[SessionDetail]:
    """
    Get detailed information about a session.
    
    Args:
        db_session: Database session.
        user_id: User ID.
        session_id: Session ID.
        
    Returns:
        Session detail or None if not found.
    """
    recipe_session = get_session_by_id(db_session, user_id, session_id)
    
    if recipe_session is None:
        return None
    
    # Parse stored JSON
    request = CookingRequest.model_validate(recipe_session.request_json)
    result = FullRecipe.model_validate(recipe_session.result_json)
    
    # Get follow-ups
    followups = list_followups(db_session, session_id)
    
    return SessionDetail(
        id=recipe_session.id,
        created_at=recipe_session.created_at,
        request=request,
        result=result,
        followups=followups
    )


def get_session_followups(
    db_session: Session,
    user_id: int,
    session_id: int
) -> List[FollowUpSummary]:
    """
    Get follow-up questions for a session.
    
    Args:
        db_session: Database session.
        user_id: User ID.
        session_id: Session ID.
        
    Returns:
        List of follow-up summaries.
    """
    # Verify user has access to this session
    recipe_session = get_session_by_id(db_session, user_id, session_id)
    
    if recipe_session is None:
        return []
    
    return list_followups(db_session, session_id)
