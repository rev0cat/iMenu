from typing import Callable, List

from backend.agents.roles import CHAIR, CHEF, NUTRITION
from backend.llm.factory import get_llm_client
from backend.models import DiscussionEvent, FollowUpResponse, FollowUpState, FullRecipe

EventCallback = Callable[[DiscussionEvent], None]
llm = get_llm_client()


def _emit(event_callback: EventCallback | None, event: DiscussionEvent) -> None:
    if event_callback:
        event_callback(event)


def load_context_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    _emit(
        event_callback,
        DiscussionEvent(
            event_type="followup_question",
            payload={"question": state.question, "dish": state.previous_recipe.dish.name},
        ),
    )
    return state


def followup_expert_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    answers: List[str] = []
    for role in (CHEF, NUTRITION):
        text = llm.generate(f"{role.name} 针对追问的建议: {state.question}")
        answers.append(text)
        _emit(
            event_callback,
            DiscussionEvent(
                event_type="expert_opinion",
                expert_name=role.name,
                payload={"comments": text},
            ),
        )
    merged_answer = "\n".join(answers)
    updated_recipe = _merge_recipe(state.previous_recipe, merged_answer)
    state.response = FollowUpResponse(answer=merged_answer, updated_recipe=updated_recipe)
    return state


def followup_output_node(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    if state.response:
        _emit(
            event_callback,
            DiscussionEvent(
                event_type="followup_answer",
                expert_name=CHAIR.name,
                payload={"answer": state.response.answer},
            ),
        )
    return state


def _merge_recipe(previous: FullRecipe, answer: str) -> FullRecipe:
    """在追问时附加一个提示步骤，示意追问已被整合。"""
    if not previous.steps:
        return previous
    extra_step = previous.steps + [
        previous.steps[-1].copy(update={
            "index": len(previous.steps),
            "title": "追问调整",
            "description": f"根据追问增加的提示: {answer[:50]}",
        })
    ]
    return previous.copy(update={"steps": extra_step, "review_rounds_used": previous.review_rounds_used + 1})

