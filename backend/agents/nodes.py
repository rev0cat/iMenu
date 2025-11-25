"""
LangGraph node functions for the expert committee workflow.
"""
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from state import OrchestratorState
from models import (
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


def request_normalizer_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Normalize the input request into standardized internal formats.
    """
    request = state.request
    
    # Normalize ingredients
    ingredients = [
        Ingredient(
            name=ing.name,
            state=ing.state,
            amount=ing.amount,
            unit=ing.unit,
            notes=ing.notes
        )
        for ing in request.ingredients
    ]
    
    # Normalize tools
    tools = [
        Tool(name=tool.name, type=tool.type)
        for tool in request.tools
    ]
    
    # Set constraints
    constraints = request.constraints
    
    # Set max review rounds
    max_rounds = request.max_review_rounds or 1
    
    # Create planning started event
    event = _create_event(
        event_type="planning_started",
        payload={
            "ingredients_count": len(ingredients),
            "tools_count": len(tools),
            "constraints": constraints.model_dump() if constraints else {},
            "max_review_rounds": max_rounds
        }
    )
    
    return {
        "ingredients": ingredients,
        "tools": tools,
        "constraints": constraints,
        "max_review_rounds": max_rounds,
        "events": [event]
    }


def base_planner_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Generate the initial dish plan based on inputs.
    """
    llm = get_llm_client()
    
    # Build context for the planner
    context = _build_context(state)
    prompt = f"""作为一位烹饪规划专家，请根据以下食材和约束条件，设计一道菜品方案。

{context}

请以JSON格式返回菜品方案（dish plan），包含：
- name: 菜品名称
- cuisine: 菜系
- rationale: 选择这道菜的理由
- high_level_steps: 高级步骤列表

同时设计详细的烹饪步骤。"""
    
    # Generate dish plan
    response = llm.generate(prompt)
    
    try:
        plan_data = json.loads(response)
        dish_plan = DishPlan(
            name=plan_data.get("name", "未命名菜品"),
            cuisine=plan_data.get("cuisine"),
            rationale=plan_data.get("rationale", "基于现有食材的合理搭配"),
            high_level_steps=plan_data.get("high_level_steps", ["准备食材", "烹饪", "装盘"])
        )
    except json.JSONDecodeError:
        # Fallback dish plan
        dish_plan = DishPlan(
            name="家常炒菜",
            cuisine="中式家常菜",
            rationale="根据现有食材进行简单搭配",
            high_level_steps=["准备食材", "烹饪", "装盘"]
        )
    
    # Generate initial cooking steps
    steps = _generate_initial_steps(state, dish_plan, llm)
    
    # Create initial plan event
    event = _create_event(
        event_type="initial_plan",
        payload={
            "dish_plan": dish_plan.model_dump(),
            "steps_count": len(steps)
        }
    )
    
    return {
        "base_dish_plan": dish_plan,
        "current_steps": steps,
        "current_round": 1,
        "events": [event]
    }


def _generate_initial_steps(
    state: OrchestratorState,
    dish_plan: DishPlan,
    llm: Any
) -> List[CookingStep]:
    """Generate initial cooking steps."""
    prompt = f"""请为「{dish_plan.name}」设计详细的烹饪步骤（cooking steps）。

高级步骤概要：
{chr(10).join(f'- {step}' for step in dish_plan.high_level_steps)}

可用食材：
{chr(10).join(f'- {ing.name} ({ing.state})' for ing in state.ingredients)}

可用工具：
{chr(10).join(f'- {tool.name}' for tool in state.tools) if state.tools else '- 常用厨房工具'}

请以JSON数组格式返回详细步骤。"""
    
    response = llm.generate(prompt)
    
    try:
        steps_data = json.loads(response)
        if isinstance(steps_data, list):
            steps = []
            for i, step_data in enumerate(steps_data):
                steps.append(CookingStep(
                    index=i + 1,
                    title=step_data.get("title", f"步骤{i+1}"),
                    description=step_data.get("description", ""),
                    actions=step_data.get("actions", []),
                    tools_used=step_data.get("tools_used", []),
                    ingredients_used=step_data.get("ingredients_used", []),
                    time_estimate_min=step_data.get("time_estimate_min"),
                    tips=step_data.get("tips"),
                    safety_notes=step_data.get("safety_notes")
                ))
            return steps
    except json.JSONDecodeError:
        pass
    
    # Fallback steps
    return [
        CookingStep(
            index=1,
            title="准备食材",
            description="将所有食材清洗干净，按需切配",
            actions=["清洗", "切配"],
            tools_used=["菜刀", "砧板"],
            ingredients_used=[ing.name for ing in state.ingredients],
            time_estimate_min=10
        ),
        CookingStep(
            index=2,
            title="烹饪",
            description="按照菜谱要求进行烹饪",
            actions=["炒制"],
            tools_used=["炒锅"],
            ingredients_used=[ing.name for ing in state.ingredients],
            time_estimate_min=15
        ),
        CookingStep(
            index=3,
            title="装盘",
            description="将烹饪好的菜品装盘",
            actions=["装盘"],
            tools_used=["盘子"],
            ingredients_used=[],
            time_estimate_min=2
        )
    ]


def _build_context(state: OrchestratorState) -> str:
    """Build context string from state."""
    parts = []
    
    # Ingredients
    if state.ingredients:
        parts.append("食材列表：")
        for ing in state.ingredients:
            ing_str = f"- {ing.name} ({ing.state})"
            if ing.amount and ing.unit:
                ing_str += f" - {ing.amount}{ing.unit}"
            if ing.notes:
                ing_str += f" - 备注: {ing.notes}"
            parts.append(ing_str)
    
    # Tools
    if state.tools:
        parts.append("\n可用工具：")
        for tool in state.tools:
            parts.append(f"- {tool.name}")
    
    # Constraints
    if state.constraints:
        parts.append("\n约束条件：")
        if state.constraints.goal:
            parts.append(f"- 目标: {state.constraints.goal}")
        if state.constraints.time_limit_min:
            parts.append(f"- 时间限制: {state.constraints.time_limit_min}分钟")
        if state.constraints.difficulty:
            parts.append(f"- 难度: {state.constraints.difficulty}")
        if state.constraints.dietary_restrictions:
            parts.append(f"- 饮食限制: {', '.join(state.constraints.dietary_restrictions)}")
    
    # User notes
    if state.request.user_notes:
        parts.append(f"\n用户备注：{state.request.user_notes}")
    
    return "\n".join(parts)


def _build_current_plan_context(state: OrchestratorState) -> str:
    """Build context string including current plan."""
    context = _build_context(state)
    
    if state.base_dish_plan:
        context += f"\n\n当前菜品方案：\n名称：{state.base_dish_plan.name}"
        context += f"\n菜系：{state.base_dish_plan.cuisine}"
        context += f"\n理由：{state.base_dish_plan.rationale}"
    
    if state.current_steps:
        context += "\n\n当前烹饪步骤："
        for step in state.current_steps:
            context += f"\n{step.index}. {step.title}: {step.description}"
    
    return context


def _create_expert_opinion_node(role_key: str):
    """Factory function to create expert opinion nodes."""
    
    def expert_opinion_node(state: OrchestratorState) -> Dict[str, Any]:
        """Generate expert opinion for the current round."""
        role = EXPERT_ROLES[role_key]
        llm = get_llm_client()
        
        context = _build_current_plan_context(state)
        prompt = get_expert_prompt(role_key, context)
        
        comments = llm.generate(prompt)
        
        opinion = ExpertOpinion(
            expert_name=role.name,
            role=role.title,
            round_index=state.current_round,
            comments=comments,
            suggested_changes_summary=f"{role.name}建议关注{role.focus_areas[0]}方面"
        )
        
        event = _create_event(
            event_type="expert_opinion",
            round_index=state.current_round,
            expert_name=role.name,
            payload={
                "opinion": opinion.model_dump()
            }
        )
        
        return {
            "expert_opinions": [opinion],
            "events": [event]
        }
    
    return expert_opinion_node


# Create individual expert opinion nodes
chef_opinion_node = _create_expert_opinion_node("chef")
nutrition_opinion_node = _create_expert_opinion_node("nutrition")
tool_process_opinion_node = _create_expert_opinion_node("tool_process")
newbie_opinion_node = _create_expert_opinion_node("newbie")
safety_opinion_node = _create_expert_opinion_node("safety")


def objections_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Generate objections between experts based on current round opinions.
    """
    llm = get_llm_client()
    
    # Get opinions from current round
    current_round_opinions = [
        op for op in state.expert_opinions
        if op.round_index == state.current_round
    ]
    
    objections = []
    events = []
    
    # Each expert can object to others
    for from_opinion in current_round_opinions:
        for to_opinion in current_round_opinions:
            if from_opinion.expert_name != to_opinion.expert_name:
                # Simulate objection logic (mock)
                prompt = f"""作为{from_opinion.expert_name}，请审视{to_opinion.expert_name}的意见：
                
{to_opinion.comments}

你是否有异议？如果有，请说明理由。以JSON格式返回：
{{"has_objection": true/false, "reason": "...", "severity": "minor/major"}}"""
                
                response = llm.generate(prompt + " objection")
                
                try:
                    objection_data = json.loads(response)
                    if objection_data.get("has_objection", False):
                        objection = ExpertObjection(
                            from_expert=from_opinion.expert_name,
                            to_expert=to_opinion.expert_name,
                            round_index=state.current_round,
                            reason=objection_data.get("reason", "存在不同意见"),
                            severity=objection_data.get("severity", "minor")
                        )
                        objections.append(objection)
                        
                        event = _create_event(
                            event_type="expert_objection",
                            round_index=state.current_round,
                            expert_name=from_opinion.expert_name,
                            target_expert=to_opinion.expert_name,
                            payload={
                                "objection": objection.model_dump()
                            }
                        )
                        events.append(event)
                except json.JSONDecodeError:
                    pass
    
    return {
        "expert_objections": objections,
        "events": events
    }


def objection_responses_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Generate responses from experts who received objections.
    """
    llm = get_llm_client()
    
    # Get objections from current round that haven't been responded to
    current_objections = [
        obj for obj in state.expert_objections
        if obj.round_index == state.current_round and obj.target_stance is None
    ]
    
    events = []
    updated_objections = []
    
    for objection in current_objections:
        prompt = f"""作为{objection.to_expert}，你收到了来自{objection.from_expert}的异议：

异议理由：{objection.reason}
严重程度：{objection.severity}

请回应这个异议。你可以选择接受(accepted)或反驳(rebutted)。"""
        
        response = llm.generate(prompt)
        
        # Randomly decide accept or rebut for mock
        import random
        stance = random.choice(["accepted", "rebutted"])
        
        objection.target_stance = stance
        objection.target_response = response if len(response) < 200 else response[:200]
        updated_objections.append(objection)
        
        event = _create_event(
            event_type="objection_response",
            round_index=state.current_round,
            expert_name=objection.to_expert,
            target_expert=objection.from_expert,
            payload={
                "stance": stance,
                "response": objection.target_response
            }
        )
        events.append(event)
    
    return {
        "events": events
    }


def chair_decision_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Chair makes final decision for the round, potentially updating the plan.
    """
    llm = get_llm_client()
    
    # Build summary of all opinions and objections
    summary_parts = ["本轮专家意见汇总："]
    
    current_opinions = [
        op for op in state.expert_opinions
        if op.round_index == state.current_round
    ]
    
    for op in current_opinions:
        summary_parts.append(f"\n{op.expert_name}：{op.comments[:100]}...")
    
    current_objections = [
        obj for obj in state.expert_objections
        if obj.round_index == state.current_round
    ]
    
    if current_objections:
        summary_parts.append("\n\n异议情况：")
        for obj in current_objections:
            summary_parts.append(
                f"\n- {obj.from_expert} 对 {obj.to_expert}: {obj.reason[:50]}... "
                f"({obj.target_stance or '待处理'})"
            )
    
    context = "\n".join(summary_parts)
    prompt = get_expert_prompt("chair", context, "请做出本轮的最终裁决。")
    
    decision = llm.generate(prompt + " chair decision")
    
    # Update objections with chair resolution
    for obj in current_objections:
        if obj.resolution is None:
            obj.resolution = f"主席裁决：考虑双方意见后，建议{obj.target_stance or '继续讨论'}。"
    
    # Determine if we should stop
    should_stop = (
        state.current_round >= state.max_review_rounds or
        len(current_objections) == 0 or
        all(obj.severity == "minor" for obj in current_objections)
    )
    
    event = _create_event(
        event_type="chair_decision",
        round_index=state.current_round,
        expert_name="主席",
        payload={
            "decision": decision,
            "should_continue": not should_stop,
            "next_round": state.current_round + 1 if not should_stop else None
        }
    )
    
    round_finished_event = _create_event(
        event_type="round_finished",
        round_index=state.current_round,
        payload={
            "opinions_count": len(current_opinions),
            "objections_count": len(current_objections),
            "should_stop": should_stop
        }
    )
    
    return {
        "should_stop": should_stop,
        "current_round": state.current_round + 1 if not should_stop else state.current_round,
        "events": [event, round_finished_event]
    }


def output_formatter_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Format the final recipe output.
    """
    # Generate tutorial markdown
    tutorial_parts = [f"# {state.base_dish_plan.name}\n"]
    
    if state.base_dish_plan.cuisine:
        tutorial_parts.append(f"**菜系**: {state.base_dish_plan.cuisine}\n")
    
    tutorial_parts.append(f"\n## 简介\n{state.base_dish_plan.rationale}\n")
    
    tutorial_parts.append("\n## 食材\n")
    for ing in state.ingredients:
        line = f"- {ing.name}"
        if ing.amount and ing.unit:
            line += f" {ing.amount}{ing.unit}"
        if ing.state != "raw":
            line += f" ({ing.state})"
        tutorial_parts.append(line)
    
    if state.tools:
        tutorial_parts.append("\n\n## 工具\n")
        for tool in state.tools:
            tutorial_parts.append(f"- {tool.name}")
    
    tutorial_parts.append("\n\n## 步骤\n")
    for step in state.current_steps:
        tutorial_parts.append(f"\n### {step.index}. {step.title}")
        tutorial_parts.append(f"\n{step.description}")
        if step.time_estimate_min:
            tutorial_parts.append(f"\n⏱ 预计时间：{step.time_estimate_min}分钟")
        if step.tips:
            tutorial_parts.append(f"\n💡 小贴士：{step.tips}")
        if step.safety_notes:
            tutorial_parts.append(f"\n⚠️ 安全提示：{step.safety_notes}")
    
    tutorial_markdown = "\n".join(tutorial_parts)
    
    # Build final recipe
    final_recipe = FullRecipe(
        dish=state.base_dish_plan,
        ingredients=state.ingredients,
        tools=state.tools,
        constraints=state.constraints or Constraints(),
        steps=state.current_steps,
        expert_opinions=state.expert_opinions,
        expert_objections=state.expert_objections,
        review_rounds_used=state.current_round,
        tutorial_markdown=tutorial_markdown
    )
    
    event = _create_event(
        event_type="final_summary",
        payload={
            "dish_name": final_recipe.dish.name,
            "steps_count": len(final_recipe.steps),
            "review_rounds_used": final_recipe.review_rounds_used,
            "expert_opinions_count": len(final_recipe.expert_opinions),
            "expert_objections_count": len(final_recipe.expert_objections)
        }
    )
    
    return {
        "final_recipe": final_recipe,
        "events": [event]
    }
