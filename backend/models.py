"""
Pydantic models for request/response and internal state.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ================== Input Models ==================

class IngredientInput(BaseModel):
    """Frontend ingredient input model."""
    name: str
    state: str = "raw"  # "raw" / "frozen" / "cooked" / "diced" etc.
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class ToolInput(BaseModel):
    """Frontend tool input model."""
    name: str
    type: Optional[str] = None


class Constraints(BaseModel):
    """Cooking constraints from user."""
    goal: Optional[str] = None  # "减脂餐" / "高蛋白" etc.
    time_limit_min: Optional[int] = None
    difficulty: Optional[str] = None  # "beginner" / "intermediate"
    dietary_restrictions: Optional[List[str]] = None


class CookingRequest(BaseModel):
    """Main cooking request from frontend."""
    ingredients: List[IngredientInput]
    tools: List[ToolInput] = []
    constraints: Constraints = Field(default_factory=Constraints)
    user_notes: Optional[str] = None
    max_review_rounds: Optional[int] = 1


# ================== Internal Standard Models ==================

class Ingredient(BaseModel):
    """Standardized ingredient for internal use."""
    name: str
    state: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class Tool(BaseModel):
    """Standardized tool for internal use."""
    name: str
    type: Optional[str] = None


# ================== Recipe Models ==================

class DishPlan(BaseModel):
    """High-level dish plan."""
    name: str
    cuisine: Optional[str] = None
    rationale: str
    high_level_steps: List[str]


class CookingStep(BaseModel):
    """Single cooking step."""
    index: int
    title: str
    description: str
    actions: List[str] = []
    tools_used: List[str] = []
    ingredients_used: List[str] = []
    time_estimate_min: Optional[float] = None
    tips: Optional[str] = None
    safety_notes: Optional[str] = None


# ================== Expert Opinion Models ==================

class ExpertOpinion(BaseModel):
    """Single expert's opinion in a round."""
    expert_name: str
    role: str
    round_index: int
    comments: str
    suggested_changes_summary: str
    updated_dish_plan: Optional[DishPlan] = None
    updated_steps: Optional[List[CookingStep]] = None


class ExpertObjection(BaseModel):
    """Expert objection with response and resolution."""
    from_expert: str
    to_expert: str
    round_index: int
    reason: str
    severity: str = "minor"  # "minor" / "major"
    target_stance: Optional[str] = None  # "accepted" / "rebutted" / None
    target_response: Optional[str] = None
    resolution: Optional[str] = None  # Chairman's resolution


# ================== Full Recipe Model ==================

class FullRecipe(BaseModel):
    """Complete recipe output."""
    dish: DishPlan
    ingredients: List[Ingredient]
    tools: List[Tool]
    constraints: Constraints
    steps: List[CookingStep]
    expert_opinions: List[ExpertOpinion] = []
    expert_objections: List[ExpertObjection] = []
    review_rounds_used: int
    tutorial_markdown: Optional[str] = None


# ================== Discussion Event Model ==================

class DiscussionEvent(BaseModel):
    """WebSocket streaming event for discussion visualization."""
    event_type: str  # "planning_started", "initial_plan", "round_started",
                     # "expert_opinion", "expert_objection", "objection_response",
                     # "chair_decision", "round_finished", "final_summary",
                     # "followup_question", "followup_answer"
    round_index: Optional[int] = None
    expert_name: Optional[str] = None
    target_expert: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    partial: Optional[bool] = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ================== Follow-up Models ==================

class FollowUpRequest(BaseModel):
    """Follow-up question request."""
    session_id: int
    question: str
    max_review_rounds: Optional[int] = 1


class FollowUpResponse(BaseModel):
    """Follow-up response."""
    answer: str
    updated_recipe: Optional[FullRecipe] = None


# ================== History Response Models ==================

class SessionSummary(BaseModel):
    """Summary of a recipe session for list view."""
    id: int
    created_at: datetime
    dish_name: Optional[str] = None
    goal: Optional[str] = None
    rounds_used: int


class FollowUpSummary(BaseModel):
    """Summary of a follow-up for list view."""
    id: int
    created_at: datetime
    question: str


class SessionDetail(BaseModel):
    """Full session detail including request and result."""
    id: int
    created_at: datetime
    request: CookingRequest
    result: FullRecipe
    followups: List[FollowUpSummary] = []
