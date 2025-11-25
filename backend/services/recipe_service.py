from typing import Callable
from backend.state import build_initial_state, EventBuffer
from backend.models import CookingRequest, DiscussionEvent, FullRecipe
from backend.graphs import recipe_graph
from backend.db import repositories

EventCallback = Callable[[DiscussionEvent], None]


def generate_recipe_sync(user_id: int, request: CookingRequest) -> FullRecipe:
    state = build_initial_state(request)
    result_state = recipe_graph.run(state)
    recipe = result_state.final_recipe
    if not recipe:
        raise ValueError("Failed to build recipe")
    session = repositories.create_session(user_id=user_id, request=request, full_recipe=recipe, rounds_used=result_state.current_round)
    repositories.save_discussion_events(session.id, [])
    return recipe


def generate_recipe_stream(
    user_id: int, request: CookingRequest, event_callback: EventCallback
) -> FullRecipe:
    state = build_initial_state(request)
    buffer = EventBuffer()

    def capture(event: DiscussionEvent):
        buffer.push(event)
        event_callback(event)

    result_state = recipe_graph.run(state, capture)
    recipe = result_state.final_recipe
    if not recipe:
        raise ValueError("Failed to build recipe")
    session = repositories.create_session(user_id=user_id, request=request, full_recipe=recipe, rounds_used=result_state.current_round)
    repositories.save_discussion_events(session.id, buffer.flush())
    return recipe

