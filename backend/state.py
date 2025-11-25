"""
Orchestrator state definitions for LangGraph workflows.
"""
from typing import Annotated, Any, List, Optional, Callable
from pydantic import BaseModel, Field
import operator

from models import (
    CookingRequest,
    Ingredient,
    Tool,
    Constraints,
    DishPlan,
    CookingStep,
    ExpertOpinion,
    ExpertObjection,
    FullRecipe,
    DiscussionEvent,
)


def add_to_list(existing: List[Any], new: Any) -> List[Any]:
    """Reducer for appending items to a list."""
    if isinstance(new, list):
        return existing + new
    return existing + [new]


class OrchestratorState(BaseModel):
    """
    State for the main recipe generation workflow.
    Used by LangGraph to track progress through the expert committee.
    """
    # Input
    request: CookingRequest
    
    # Normalized data
    ingredients: List[Ingredient] = Field(default_factory=list)
    tools: List[Tool] = Field(default_factory=list)
    constraints: Optional[Constraints] = None
    
    # Current plan
    base_dish_plan: Optional[DishPlan] = None
    current_steps: List[CookingStep] = Field(default_factory=list)
    
    # Expert opinions and objections
    expert_opinions: Annotated[List[ExpertOpinion], add_to_list] = Field(default_factory=list)
    expert_objections: Annotated[List[ExpertObjection], add_to_list] = Field(default_factory=list)
    
    # Output
    final_recipe: Optional[FullRecipe] = None
    
    # Control flow
    current_round: int = 0
    max_review_rounds: int = 1
    should_stop: bool = False
    
    # Event streaming
    events: Annotated[List[DiscussionEvent], add_to_list] = Field(default_factory=list)
    
    # User ID for database operations
    user_id: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True


class FollowUpState(BaseModel):
    """
    State for follow-up question workflow.
    """
    # Context
    session_id: int
    original_request: CookingRequest
    original_recipe: FullRecipe
    
    # Follow-up input
    question: str
    max_review_rounds: int = 1
    current_round: int = 0
    
    # Expert processing
    expert_opinions: Annotated[List[ExpertOpinion], add_to_list] = Field(default_factory=list)
    expert_objections: Annotated[List[ExpertObjection], add_to_list] = Field(default_factory=list)
    
    # Output
    answer: Optional[str] = None
    updated_recipe: Optional[FullRecipe] = None
    should_stop: bool = False
    
    # Event streaming
    events: Annotated[List[DiscussionEvent], add_to_list] = Field(default_factory=list)
    
    # User ID
    user_id: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True
