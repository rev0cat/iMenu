from typing import Callable
from typing import Callable

from backend.state import build_followup_state, EventBuffer
from backend.models import DiscussionEvent, FollowUpResponse, CookingRequest, FullRecipe
from backend.graphs import followup_graph
from backend.db import repositories

EventCallback = Callable[[DiscussionEvent], None]


def followup_sync(user_id: int, session_id: int, question: str, max_review_rounds: int) -> FollowUpResponse:
    session = repositories.get_session_by_id(user_id, session_id)
    if not session:
        raise ValueError("Session not found")
    cooking_request = CookingRequest(**session.request_json)
    previous_recipe = FullRecipe(**session.result_json)
    state = build_followup_state(
        request=cooking_request,
        recipe=previous_recipe,
        question=question,
        max_rounds=max_review_rounds,
    )
    result_state = followup_graph.run(state)
    response = result_state.response
    if not response:
        raise ValueError("Failed to generate follow-up response")
    repositories.append_followup_record(session_id, question, response)
    return response


def followup_stream(
    user_id: int, session_id: int, question: str, max_review_rounds: int, event_callback: EventCallback
) -> FollowUpResponse:
    session = repositories.get_session_by_id(user_id, session_id)
    if not session:
        raise ValueError("Session not found")
    cooking_request = CookingRequest(**session.request_json)
    previous_recipe = FullRecipe(**session.result_json)
    state = build_followup_state(
        request=cooking_request,
        recipe=previous_recipe,
        question=question,
        max_rounds=max_review_rounds,
    )
    buffer = EventBuffer()

    def capture(event: DiscussionEvent):
        buffer.push(event)
        event_callback(event)

    result_state = followup_graph.run(state, capture)
    response = result_state.response
    if not response:
        raise ValueError("Failed to generate follow-up response")
    repositories.append_followup_record(session_id, question, response)
    repositories.save_discussion_events(session_id, buffer.flush())
    return response

