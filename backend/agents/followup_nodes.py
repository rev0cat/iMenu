from typing import Callable
from backend.models import DiscussionEvent, FollowUpState, FollowUpResponse
from backend.agents.roles import CHEF, NUTRITION, CHAIR
from backend.llm.mock_client import MockLLMClient

EventCallback = Callable[[DiscussionEvent], None]
llm = MockLLMClient()


def load_context_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    if event_callback:
        event_callback(
            DiscussionEvent(
                event_type="followup_question",
                payload={"question": state.question},
            )
        )
    return state


def followup_expert_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    answers = []
    for role in (CHEF, NUTRITION):
        text = llm.generate(f"{role.name} follow-up: {state.question}")
        answers.append(text)
        if event_callback:
            event_callback(
                DiscussionEvent(
                    event_type="expert_opinion",
                    expert_name=role.name,
                    payload={"comments": text},
                )
            )
    summary = " \n".join(answers)
    state.response = FollowUpResponse(answer=summary, updated_recipe=state.previous_recipe)
    return state


def followup_output_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    if event_callback and state.response:
        event_callback(
            DiscussionEvent(
                event_type="followup_answer",
                expert_name=CHAIR.name,
                payload={"answer": state.response.answer},
            )
        )
    return state

