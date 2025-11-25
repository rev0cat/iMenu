from typing import Any, Dict, Iterable, List, Optional
from pydantic import BaseModel, Field


class IngredientInput(BaseModel):
    name: str
    state: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class ToolInput(BaseModel):
    name: str
    type: Optional[str] = None


class Constraints(BaseModel):
    goal: Optional[str] = None
    time_limit_min: Optional[int] = None
    difficulty: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None


class CookingRequest(BaseModel):
    ingredients: List[IngredientInput]
    tools: List[ToolInput]
    constraints: Constraints
    user_notes: Optional[str] = None
    max_review_rounds: Optional[int] = 1


class Ingredient(BaseModel):
    name: str
    state: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class Tool(BaseModel):
    name: str
    type: Optional[str] = None


class DishPlan(BaseModel):
    name: str
    cuisine: Optional[str] = None
    rationale: str
    high_level_steps: List[str]


class CookingStep(BaseModel):
    index: int
    title: str
    description: str
    actions: List[str]
    tools_used: List[str]
    ingredients_used: List[str]
    time_estimate_min: Optional[float] = None
    tips: Optional[str] = None
    safety_notes: Optional[str] = None


class ExpertOpinion(BaseModel):
    expert_name: str
    role: str
    round_index: int
    comments: str
    suggested_changes_summary: str
    updated_dish_plan: Optional[DishPlan] = None
    updated_steps: Optional[List[CookingStep]] = None


class ExpertObjection(BaseModel):
    from_expert: str
    to_expert: str
    round_index: int
    reason: str
    severity: str
    target_stance: Optional[str] = None
    target_response: Optional[str] = None
    resolution: Optional[str] = None


class FullRecipe(BaseModel):
    dish: DishPlan
    ingredients: List[Ingredient]
    tools: List[Tool]
    constraints: Constraints
    steps: List[CookingStep]
    expert_opinions: List[ExpertOpinion]
    expert_objections: List[ExpertObjection]
    review_rounds_used: int
    tutorial_markdown: Optional[str] = None


class OrchestratorState(BaseModel):
    request: CookingRequest
    ingredients: List[Ingredient]
    tools: List[Tool]
    constraints: Optional[Constraints]
    base_dish_plan: Optional[DishPlan]
    current_steps: List[CookingStep]
    expert_opinions: List[ExpertOpinion]
    expert_objections: List[ExpertObjection]
    final_recipe: Optional[FullRecipe]
    current_round: int
    max_review_rounds: int
    should_stop: bool = False


class DiscussionEvent(BaseModel):
    event_type: str
    round_index: Optional[int] = None
    expert_name: Optional[str] = None
    target_expert: Optional[str] = None
    payload: Dict[str, Any]
    partial: Optional[bool] = False


class FollowUpRequest(BaseModel):
    session_id: int
    question: str
    max_review_rounds: Optional[int] = 1


class FollowUpResponse(BaseModel):
    answer: str
    updated_recipe: Optional[FullRecipe] = None


class FollowUpState(BaseModel):
    request: CookingRequest
    previous_recipe: FullRecipe
    question: str
    max_review_rounds: int = 1
    events: List[DiscussionEvent] = Field(default_factory=list)
    response: Optional[FollowUpResponse] = None
