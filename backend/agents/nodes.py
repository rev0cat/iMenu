from typing import Callable, List
from backend import models
from backend.agents import roles
from backend.llm.mock_client import get_llm_client

DiscussionCallback = Callable[[models.DiscussionEvent], None]


def request_normalizer_node(state: models.OrchestratorState) -> models.OrchestratorState:
    return state


def base_planner_node(state: models.OrchestratorState) -> models.OrchestratorState:
    llm = get_llm_client("mock")
    plan_text = llm.generate("Draft a base dish plan")
    dish = models.DishPlan(
        name="LLM Draft Dish",
        cuisine="fusion",
        rationale=plan_text,
        high_level_steps=["Prepare ingredients", "Cook", "Plate"],
    )
    step = models.CookingStep(
        index=1,
        title="Initial cooking",
        description="Combine ingredients and cook thoroughly.",
        actions=["mix", "heat"],
        tools_used=[tool.name for tool in state.tools],
        ingredients_used=[ing.name for ing in state.ingredients],
    )
    state.base_dish_plan = dish
    state.current_steps = [step]
    return state


def _opinion_from_role(state: models.OrchestratorState, role: str, round_index: int) -> models.ExpertOpinion:
    llm = get_llm_client("mock")
    comments = llm.generate(f"{role} review for round {round_index}")
    return models.ExpertOpinion(
        expert_name=role,
        role=role,
        round_index=round_index,
        comments=comments,
        suggested_changes_summary="Keep improving",
        updated_dish_plan=state.base_dish_plan,
        updated_steps=state.current_steps,
    )


def chef_opinion_node(state: models.OrchestratorState) -> models.OrchestratorState:
    opinion = _opinion_from_role(state, roles.CHEF, state.current_round)
    state.expert_opinions.append(opinion)
    return state


def nutrition_opinion_node(state: models.OrchestratorState) -> models.OrchestratorState:
    opinion = _opinion_from_role(state, roles.NUTRITION, state.current_round)
    state.expert_opinions.append(opinion)
    return state


def tool_process_opinion_node(state: models.OrchestratorState) -> models.OrchestratorState:
    opinion = _opinion_from_role(state, roles.TOOLS, state.current_round)
    state.expert_opinions.append(opinion)
    return state


def newbie_opinion_node(state: models.OrchestratorState) -> models.OrchestratorState:
    opinion = _opinion_from_role(state, roles.COACH, state.current_round)
    state.expert_opinions.append(opinion)
    return state


def safety_opinion_node(state: models.OrchestratorState) -> models.OrchestratorState:
    opinion = _opinion_from_role(state, roles.SAFETY, state.current_round)
    state.expert_opinions.append(opinion)
    return state


def objections_node(state: models.OrchestratorState) -> models.OrchestratorState:
    if len(state.expert_opinions) < 2:
        return state
    first, second = state.expert_opinions[-2:]
    objection = models.ExpertObjection(
        from_expert=first.expert_name,
        to_expert=second.expert_name,
        round_index=state.current_round,
        reason="Suggest alternative seasoning",
        severity="minor",
    )
    state.expert_objections.append(objection)
    return state


def objection_responses_node(state: models.OrchestratorState) -> models.OrchestratorState:
    for objection in state.expert_objections:
        objection.target_stance = "accepted"
        objection.target_response = "Will adjust seasoning"
    return state


def chair_decision_node(state: models.OrchestratorState) -> models.OrchestratorState:
    llm = get_llm_client("mock")
    summary = llm.generate("Summarize committee findings")
    should_stop = state.current_round + 1 >= state.max_review_rounds
    state.should_stop = should_stop
    state.current_round += 1
    tutorial_md = "\n".join([f"{step.index}. {step.title}: {step.description}" for step in state.current_steps])
    state.final_recipe = models.FullRecipe(
        dish=state.base_dish_plan or models.DishPlan(
            name="Fallback Dish",
            cuisine=None,
            rationale="",
            high_level_steps=[],
        ),
        ingredients=state.ingredients,
        tools=state.tools,
        constraints=state.constraints or state.request.constraints,
        steps=state.current_steps,
        expert_opinions=state.expert_opinions,
        expert_objections=state.expert_objections,
        review_rounds_used=state.current_round,
        tutorial_markdown=summary + "\n" + tutorial_md,
    )
    return state


def output_formatter_node(state: models.OrchestratorState) -> models.OrchestratorState:
    return state
