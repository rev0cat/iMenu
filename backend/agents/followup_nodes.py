"""
LangGraph nodes for follow-up question processing.
"""
import json
from typing import Any, Dict, Optional
from datetime import datetime

from state import FollowUpState
from models import (
    DishPlan,
    CookingStep,
    ExpertOpinion,
    FullRecipe,
    DiscussionEvent,
    FollowUpResponse,
)
from agents.roles import EXPERT_ROLES, get_expert_prompt
from llm import get_llm_client


def _create_event(
    event_type: str,
    round_index: Optional[int] = None,
    expert_name: Optional[str] = None,
    target_expert: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    partial: bool = False
) -> DiscussionEvent:
    """Helper to create a DiscussionEvent."""
    return DiscussionEvent(
        event_type=event_type,
        round_index=round_index,
        expert_name=expert_name,
        target_expert=target_expert,
        payload=payload or {},
        partial=partial,
        timestamp=datetime.utcnow()
    )


def load_context_node(state: FollowUpState) -> Dict[str, Any]:
    """
    Load and prepare context for follow-up processing.
    """
    # Create event for follow-up question
    event = _create_event(
        event_type="followup_question",
        payload={
            "session_id": state.session_id,
            "question": state.question,
            "original_dish": state.original_recipe.dish.name
        }
    )
    
    return {
        "current_round": 1,
        "events": [event]
    }


def _build_followup_context(state: FollowUpState) -> str:
    """Build context string for follow-up processing."""
    recipe = state.original_recipe
    
    parts = [
        f"原始菜品：{recipe.dish.name}",
        f"菜系：{recipe.dish.cuisine or '未指定'}",
        f"\n原始步骤概要：",
    ]
    
    for step in recipe.steps[:5]:  # First 5 steps for context
        parts.append(f"- {step.title}: {step.description[:50]}...")
    
    parts.append(f"\n用户追问：{state.question}")
    
    return "\n".join(parts)


def followup_chef_node(state: FollowUpState) -> Dict[str, Any]:
    """Chef expert provides input on follow-up question."""
    llm = get_llm_client()
    role = EXPERT_ROLES["chef"]
    
    context = _build_followup_context(state)
    prompt = f"""作为{role.name}，请针对用户的追问提供专业意见。

{context}

请从烹饪技术角度回答用户的问题。"""
    
    response = llm.generate(prompt + " follow-up")
    
    opinion = ExpertOpinion(
        expert_name=role.name,
        role=role.title,
        round_index=state.current_round,
        comments=response,
        suggested_changes_summary="针对追问的烹饪建议"
    )
    
    event = _create_event(
        event_type="expert_opinion",
        round_index=state.current_round,
        expert_name=role.name,
        payload={"opinion": opinion.model_dump()}
    )
    
    return {
        "expert_opinions": [opinion],
        "events": [event]
    }


def followup_nutrition_node(state: FollowUpState) -> Dict[str, Any]:
    """Nutrition expert provides input on follow-up question."""
    llm = get_llm_client()
    role = EXPERT_ROLES["nutrition"]
    
    context = _build_followup_context(state)
    prompt = f"""作为{role.name}，请针对用户的追问提供专业意见。

{context}

请从营养学角度回答用户的问题。"""
    
    response = llm.generate(prompt + " follow-up")
    
    opinion = ExpertOpinion(
        expert_name=role.name,
        role=role.title,
        round_index=state.current_round,
        comments=response,
        suggested_changes_summary="针对追问的营养建议"
    )
    
    event = _create_event(
        event_type="expert_opinion",
        round_index=state.current_round,
        expert_name=role.name,
        payload={"opinion": opinion.model_dump()}
    )
    
    return {
        "expert_opinions": [opinion],
        "events": [event]
    }


def followup_chair_node(state: FollowUpState) -> Dict[str, Any]:
    """Chair synthesizes expert opinions into final answer."""
    llm = get_llm_client()
    
    # Gather opinions from current round
    current_opinions = [
        op for op in state.expert_opinions
        if op.round_index == state.current_round
    ]
    
    context_parts = [
        f"用户追问：{state.question}",
        f"\n原始菜品：{state.original_recipe.dish.name}",
        "\n\n专家意见汇总："
    ]
    
    for op in current_opinions:
        context_parts.append(f"\n{op.expert_name}：{op.comments}")
    
    context = "\n".join(context_parts)
    
    prompt = f"""作为专家委员会主席，请综合各位专家的意见，为用户提供一个完整的回答。

{context}

请提供一个清晰、有帮助的回答。"""
    
    answer = llm.generate(prompt + " follow-up")
    
    # Determine if recipe needs update based on question
    needs_update = any(keyword in state.question.lower() for keyword in [
        "修改", "改变", "调整", "换", "替换", "增加", "减少", "删除"
    ])
    
    updated_recipe = None
    if needs_update:
        # Create a slightly modified recipe
        updated_recipe = state.original_recipe.model_copy(deep=True)
        # Add a note about the modification
        if updated_recipe.dish.rationale:
            updated_recipe.dish.rationale += f"\n\n[更新] 根据用户追问进行了调整。"
    
    event = _create_event(
        event_type="followup_answer",
        expert_name="主席",
        payload={
            "answer": answer,
            "has_recipe_update": updated_recipe is not None
        }
    )
    
    return {
        "answer": answer,
        "updated_recipe": updated_recipe,
        "should_stop": True,
        "events": [event]
    }


def followup_output_node(state: FollowUpState) -> Dict[str, Any]:
    """Format the final follow-up response."""
    # This node mainly ensures the state is properly formatted
    # The actual answer is already set by chair_node
    
    return {
        "should_stop": True
    }
