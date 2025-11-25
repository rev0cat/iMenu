from typing import Callable, List
from backend import models
from backend.db import repositories
from backend.db.session import session_scope
from backend.graphs.recipe_graph import recipe_graph
from backend.state import StateFactory


def generate_recipe_sync(user_id: int, request: models.CookingRequest) -> models.FullRecipe:
    state = StateFactory.new_orchestrator(request)
    final_state: models.OrchestratorState = recipe_graph.invoke(state)
    recipe = final_state.final_recipe or models.FullRecipe(
        dish=final_state.base_dish_plan,
        ingredients=final_state.ingredients,
        tools=final_state.tools,
        constraints=final_state.constraints or request.constraints,
        steps=final_state.current_steps,
        expert_opinions=final_state.expert_opinions,
        expert_objections=final_state.expert_objections,
        review_rounds_used=final_state.current_round,
    )
    with session_scope() as session:
        repositories.create_session(session, user_id, request, recipe)
    return recipe


def generate_recipe_stream(
    user_id: int, request: models.CookingRequest, event_callback: Callable[[models.DiscussionEvent], None]
) -> models.FullRecipe:
    state = StateFactory.new_orchestrator(request)
    events: List[models.DiscussionEvent] = []
    for update in recipe_graph.astream(state):
        if isinstance(update, models.OrchestratorState):
            event = models.DiscussionEvent(
                event_type="round_started",
                round_index=update.current_round,
                payload={"message": "Round started"},
            )
            events.append(event)
            event_callback(event)
    final_state: models.OrchestratorState = recipe_graph.invoke(state)
    recipe = final_state.final_recipe or models.FullRecipe(
        dish=final_state.base_dish_plan,
        ingredients=final_state.ingredients,
        tools=final_state.tools,
        constraints=final_state.constraints or request.constraints,
        steps=final_state.current_steps,
        expert_opinions=final_state.expert_opinions,
        expert_objections=final_state.expert_objections,
        review_rounds_used=final_state.current_round,
    )
    with session_scope() as session:
        record = repositories.create_session(session, user_id, request, recipe)
        repositories.save_discussion_events(session, record.id, events)
    return recipe
