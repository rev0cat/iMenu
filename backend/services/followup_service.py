from typing import Callable, List
from backend import models
from backend.db import repositories
from backend.db.session import session_scope
from backend.graphs.followup_graph import followup_graph
from backend.state import StateFactory


def followup_sync(user_id: int, session_id: int, question: str, max_review_rounds: int) -> models.FollowUpResponse:
    with session_scope() as session:
        session_record = repositories.get_session_by_id(session, user_id, session_id)
        if not session_record:
            raise ValueError("Session not found")
        request = models.CookingRequest(**session_record.request_json)
        recipe = models.FullRecipe(**session_record.result_json)
        state = StateFactory.new_followup(request, recipe, question, max_review_rounds)
        response: models.FollowUpResponse = followup_graph.invoke(state)
        repositories.append_followup_record(session, session_id, question, response)
        return response


def followup_stream(
    user_id: int,
    session_id: int,
    question: str,
    max_review_rounds: int,
    event_callback: Callable[[models.DiscussionEvent], None],
) -> models.FollowUpResponse:
    with session_scope() as session:
        session_record = repositories.get_session_by_id(session, user_id, session_id)
        if not session_record:
            raise ValueError("Session not found")
        request = models.CookingRequest(**session_record.request_json)
        recipe = models.FullRecipe(**session_record.result_json)
        state = StateFactory.new_followup(request, recipe, question, max_review_rounds)
        events: List[models.DiscussionEvent] = []
        for update in followup_graph.astream(state):
            if isinstance(update, models.FollowUpState):
                event = models.DiscussionEvent(
                    event_type="followup_question",
                    payload={"text": question},
                )
                events.append(event)
                event_callback(event)
        response: models.FollowUpResponse = followup_graph.invoke(state)
        repositories.append_followup_record(session, session_id, question, response)
        return response
