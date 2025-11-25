from typing import List
from .models import (
    CookingRequest,
    DiscussionEvent,
    FollowUpState,
    Ingredient,
    Tool,
    Constraints,
    CookingStep,
    DishPlan,
    ExpertOpinion,
    ExpertObjection,
    FullRecipe,
    OrchestratorState,
)


def build_initial_state(request: CookingRequest) -> OrchestratorState:
    ingredients = [Ingredient(**ing.dict()) for ing in request.ingredients]
    tools = [Tool(**tool.dict()) for tool in request.tools]
    return OrchestratorState(
        request=request,
        ingredients=ingredients,
        tools=tools,
        constraints=request.constraints,
        base_dish_plan=None,
        current_steps=[],
        expert_opinions=[],
        expert_objections=[],
        final_recipe=None,
        current_round=0,
        max_review_rounds=request.max_review_rounds or 1,
        should_stop=False,
    )


def build_followup_state(request: CookingRequest, recipe: FullRecipe, question: str, max_rounds: int) -> FollowUpState:
    return FollowUpState(
        request=request,
        previous_recipe=recipe,
        question=question,
        max_review_rounds=max_rounds,
        events=[],
        response=None,
    )


class EventBuffer:
    """In-memory buffer used to collect DiscussionEvents before persistence."""

    def __init__(self) -> None:
        self.events: List[DiscussionEvent] = []

    def push(self, event: DiscussionEvent) -> None:
        self.events.append(event)

    def flush(self) -> List[DiscussionEvent]:
        events = list(self.events)
        self.events.clear()
        return events
