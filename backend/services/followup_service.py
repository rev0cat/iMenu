"""
Follow-up question service.
"""
from typing import Callable, List, Optional
from sqlmodel import Session

from models import (
    CookingRequest,
    FullRecipe,
    DiscussionEvent,
    FollowUpRequest,
    FollowUpResponse,
)
from graphs.followup_graph import run_followup_graph, run_followup_graph_stream
from db.repositories import get_session_by_id, append_followup_record


def followup_sync(
    db_session: Session,
    user_id: int,
    session_id: int,
    question: str,
    max_review_rounds: int = 1
) -> FollowUpResponse:
    """
    Process a follow-up question synchronously.
    
    Args:
        db_session: Database session.
        user_id: ID of the requesting user.
        session_id: ID of the original recipe session.
        question: The follow-up question.
        max_review_rounds: Maximum review rounds.
        
    Returns:
        FollowUpResponse with answer and optional updated recipe.
    """
    # Get the original session
    recipe_session = get_session_by_id(db_session, user_id, session_id)
    
    if recipe_session is None:
        return FollowUpResponse(
            answer="找不到指定的会话记录，请确认会话ID是否正确。"
        )
    
    # Parse original request and recipe
    original_request = CookingRequest.model_validate(recipe_session.request_json)
    original_recipe = FullRecipe.model_validate(recipe_session.result_json)
    
    # Run the follow-up graph
    final_state = run_followup_graph(
        session_id=session_id,
        original_request=original_request,
        original_recipe=original_recipe,
        question=question,
        max_review_rounds=max_review_rounds,
        user_id=user_id
    )
    
    # Create response
    response = FollowUpResponse(
        answer=final_state.answer or "专家委员会无法提供有效答复，请重新提问。",
        updated_recipe=final_state.updated_recipe
    )
    
    # Save to database
    append_followup_record(db_session, session_id, question, response)
    
    return response


def followup_stream(
    db_session: Session,
    user_id: int,
    session_id: int,
    question: str,
    event_callback: Callable[[DiscussionEvent], None],
    max_review_rounds: int = 1
) -> FollowUpResponse:
    """
    Process a follow-up question with streaming events.
    
    Args:
        db_session: Database session.
        user_id: ID of the requesting user.
        session_id: ID of the original recipe session.
        question: The follow-up question.
        event_callback: Callback for streaming discussion events.
        max_review_rounds: Maximum review rounds.
        
    Returns:
        FollowUpResponse with answer and optional updated recipe.
    """
    # Get the original session
    recipe_session = get_session_by_id(db_session, user_id, session_id)
    
    if recipe_session is None:
        error_response = FollowUpResponse(
            answer="找不到指定的会话记录，请确认会话ID是否正确。"
        )
        # Send error event
        error_event = DiscussionEvent(
            event_type="followup_answer",
            payload={"answer": error_response.answer, "error": True}
        )
        event_callback(error_event)
        return error_response
    
    # Parse original request and recipe
    original_request = CookingRequest.model_validate(recipe_session.request_json)
    original_recipe = FullRecipe.model_validate(recipe_session.result_json)
    
    # Collect events
    all_events: List[DiscussionEvent] = []
    
    def wrapped_callback(event: DiscussionEvent):
        all_events.append(event)
        event_callback(event)
    
    # Run the follow-up graph with streaming
    final_state = run_followup_graph_stream(
        session_id=session_id,
        original_request=original_request,
        original_recipe=original_recipe,
        question=question,
        event_callback=wrapped_callback,
        max_review_rounds=max_review_rounds,
        user_id=user_id
    )
    
    # Create response
    response = FollowUpResponse(
        answer=final_state.answer or "专家委员会无法提供有效答复，请重新提问。",
        updated_recipe=final_state.updated_recipe
    )
    
    # Save to database
    append_followup_record(db_session, session_id, question, response)
    
    return response
