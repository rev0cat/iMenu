"""
Recipe generation service.
"""
from typing import Callable, List, Optional
from sqlmodel import Session

from models import CookingRequest, FullRecipe, DiscussionEvent
from graphs.recipe_graph import run_recipe_graph, run_recipe_graph_stream
from db.repositories import create_recipe_session, save_discussion_events


def generate_recipe_sync(
    db_session: Session,
    user_id: int,
    request: CookingRequest
) -> FullRecipe:
    """
    Generate a recipe synchronously.
    
    Args:
        db_session: Database session.
        user_id: ID of the requesting user.
        request: Cooking request.
        
    Returns:
        Generated FullRecipe.
    """
    # Run the recipe generation graph
    final_state = run_recipe_graph(request, user_id)
    
    # Extract the final recipe
    final_recipe = final_state.final_recipe
    
    if final_recipe is None:
        # Create a minimal recipe if graph failed
        from models import DishPlan, Ingredient, Tool, Constraints, CookingStep
        final_recipe = FullRecipe(
            dish=DishPlan(
                name="生成失败",
                rationale="菜谱生成过程出现问题",
                high_level_steps=["请重试"]
            ),
            ingredients=[],
            tools=[],
            constraints=Constraints(),
            steps=[],
            review_rounds_used=0
        )
    
    # Save to database
    recipe_session = create_recipe_session(
        db_session,
        user_id=user_id,
        request=request,
        full_recipe=final_recipe,
        rounds_used=final_recipe.review_rounds_used
    )
    
    # Save discussion events
    if final_state.events:
        save_discussion_events(db_session, recipe_session.id, final_state.events)
    
    return final_recipe


def generate_recipe_stream(
    db_session: Session,
    user_id: int,
    request: CookingRequest,
    event_callback: Callable[[DiscussionEvent], None]
) -> FullRecipe:
    """
    Generate a recipe with streaming events.
    
    Args:
        db_session: Database session.
        user_id: ID of the requesting user.
        request: Cooking request.
        event_callback: Callback for streaming discussion events.
        
    Returns:
        Generated FullRecipe.
    """
    # Collect all events for later saving
    all_events: List[DiscussionEvent] = []
    
    def wrapped_callback(event: DiscussionEvent):
        """Wrap callback to collect events and forward them."""
        all_events.append(event)
        event_callback(event)
    
    # Run the recipe generation graph with streaming
    final_state = run_recipe_graph_stream(request, wrapped_callback, user_id)
    
    # Extract the final recipe
    final_recipe = final_state.final_recipe
    
    if final_recipe is None:
        from models import DishPlan, Ingredient, Tool, Constraints, CookingStep
        final_recipe = FullRecipe(
            dish=DishPlan(
                name="生成失败",
                rationale="菜谱生成过程出现问题",
                high_level_steps=["请重试"]
            ),
            ingredients=[],
            tools=[],
            constraints=Constraints(),
            steps=[],
            review_rounds_used=0
        )
    
    # Save to database
    recipe_session = create_recipe_session(
        db_session,
        user_id=user_id,
        request=request,
        full_recipe=final_recipe,
        rounds_used=final_recipe.review_rounds_used
    )
    
    # Save discussion events
    if all_events:
        save_discussion_events(db_session, recipe_session.id, all_events)
    
    return final_recipe
