from typing import Callable, List
from backend.models import (
    DiscussionEvent,
    OrchestratorState,
    ExpertOpinion,
    ExpertObjection,
    DishPlan,
    CookingStep,
    FullRecipe,
)
from backend.agents.roles import ALL_EXPERTS, CHAIR
from backend.llm.mock_client import MockLLMClient

EventCallback = Callable[[DiscussionEvent], None]
llm = MockLLMClient()


def emit(event_callback: EventCallback, event: DiscussionEvent) -> None:
    if event_callback:
        event_callback(event)


def request_normalizer_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    emit(
        event_callback,
        DiscussionEvent(event_type="planning_started", payload={"notes": state.request.user_notes or ""}),
    )
    return state


def base_planner_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    rationale = llm.generate("Draft a base dish plan")
    state.base_dish_plan = DishPlan(
        name="Expert Committee Dish",
        cuisine="Fusion",
        rationale=rationale,
        high_level_steps=["Prepare ingredients", "Cook", "Plate"],
    )
    state.current_steps = [
        CookingStep(
            index=0,
            title="Prep",
            description="Chop and marinate as needed.",
            actions=["Chop", "Marinate"],
            tools_used=[t.name for t in state.tools],
            ingredients_used=[i.name for i in state.ingredients],
            time_estimate_min=10,
        )
    ]
    emit(
        event_callback,
        DiscussionEvent(
            event_type="initial_plan",
            payload={"dish": state.base_dish_plan.dict(), "steps": [s.dict() for s in state.current_steps]},
        ),
    )
    return state


def _opinion_for_role(role_name: str, state: OrchestratorState, round_index: int) -> ExpertOpinion:
    comments = llm.generate(f"{role_name} review round {round_index}")
    return ExpertOpinion(
        expert_name=role_name,
        role=role_name,
        round_index=round_index,
        comments=comments,
        suggested_changes_summary="Minor adjustments",
        updated_dish_plan=state.base_dish_plan,
        updated_steps=state.current_steps,
    )


def expert_opinion_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    opinions: List[ExpertOpinion] = []
    for role in ALL_EXPERTS:
        opinion = _opinion_for_role(role.name, state, state.current_round)
        opinions.append(opinion)
        emit(
            event_callback,
            DiscussionEvent(
                event_type="expert_opinion",
                round_index=state.current_round,
                expert_name=role.name,
                payload={"comments": opinion.comments},
            ),
        )
    state.expert_opinions.extend(opinions)
    return state


def objections_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    objections: List[ExpertObjection] = []
    for opinion in state.expert_opinions[-len(ALL_EXPERTS) :]:
        objection = ExpertObjection(
            from_expert=CHAIR.name,
            to_expert=opinion.expert_name,
            round_index=state.current_round,
            reason="Ensure clarity",
            severity="minor",
            target_stance="accepted",
            target_response="Acknowledged",
            resolution="Incorporated",
        )
        objections.append(objection)
        emit(
            event_callback,
            DiscussionEvent(
                event_type="expert_objection",
                round_index=state.current_round,
                expert_name=CHAIR.name,
                target_expert=opinion.expert_name,
                payload={"reason": objection.reason},
            ),
        )
    state.expert_objections.extend(objections)
    return state


def chair_decision_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    state.current_round += 1
    should_stop = state.current_round >= state.max_review_rounds
    state.should_stop = should_stop
    emit(
        event_callback,
        DiscussionEvent(
            event_type="chair_decision",
            round_index=state.current_round,
            expert_name=CHAIR.name,
            payload={"should_stop": should_stop},
        ),
    )
    return state


def output_formatter_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    state.final_recipe = state.final_recipe or _build_full_recipe(state)
    emit(
        event_callback,
        DiscussionEvent(
            event_type="final_summary",
            payload={"dish": state.final_recipe.dish.name if state.final_recipe else ""},
        ),
    )
    return state


def _build_full_recipe(state: OrchestratorState) -> FullRecipe:
    return FullRecipe(
        dish=state.base_dish_plan,
        ingredients=state.ingredients,
        tools=state.tools,
        constraints=state.constraints or state.request.constraints,
        steps=state.current_steps,
        expert_opinions=state.expert_opinions,
        expert_objections=state.expert_objections,
        review_rounds_used=state.current_round,
        tutorial_markdown="## Steps\n1. Prep\n2. Cook\n3. Serve",
    )

