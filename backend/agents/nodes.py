from typing import Callable, List

from backend.agents.roles import ALL_EXPERTS, CHAIR
from backend.llm.factory import get_llm_client
from backend.models import (
    CookingStep,
    DiscussionEvent,
    DishPlan,
    ExpertObjection,
    ExpertOpinion,
    FullRecipe,
    OrchestratorState,
)

EventCallback = Callable[[DiscussionEvent], None]
llm = get_llm_client()


def emit(event_callback: EventCallback, event: DiscussionEvent) -> None:
    if event_callback:
        event_callback(event)


def request_normalizer_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    emit(
        event_callback,
        DiscussionEvent(
            event_type="planning_started",
            payload={
                "notes": state.request.user_notes or "",
                "ingredients": [i.name for i in state.ingredients],
                "constraints": state.request.constraints.dict(),
            },
        ),
    )
    return state


def base_planner_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    goal_hint = state.request.constraints.goal or "家常菜"
    rationale = llm.generate(f"为{goal_hint}生成基础菜谱思路")
    state.base_dish_plan = DishPlan(
        name=f"{goal_hint}创意菜",
        cuisine="Fusion",
        rationale=rationale,
        high_level_steps=["准备食材", "完成主烹饪", "装盘出菜"],
    )
    state.current_steps = [
        CookingStep(
            index=0,
            title="准备",
            description="根据约束清洗、切配、腌制。",
            actions=["清洗", "切块", "腌制"],
            tools_used=[t.name for t in state.tools],
            ingredients_used=[i.name for i in state.ingredients],
            time_estimate_min=10,
            tips="提前称量好调味料。",
        ),
        CookingStep(
            index=1,
            title="烹饪",
            description="组合炒/煮流程，兼顾火候与健康。",
            actions=["热锅", "主烹饪", "收汁"],
            tools_used=[t.name for t in state.tools],
            ingredients_used=[i.name for i in state.ingredients],
            time_estimate_min=state.request.constraints.time_limit_min or 15,
            safety_notes="注意热油和蒸汽安全。",
        ),
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
    comments = llm.generate(f"{role_name} 第{round_index + 1}轮审阅: {state.base_dish_plan.name}")
    step_adjustments = [
        step.copy(update={"tips": f"{role_name} 建议：{comments[:20]}"}) for step in state.current_steps
    ]
    return ExpertOpinion(
        expert_name=role_name,
        role=role_name,
        round_index=round_index,
        comments=comments,
        suggested_changes_summary="根据角色增加了细化描述",
        updated_dish_plan=state.base_dish_plan,
        updated_steps=step_adjustments,
    )


def expert_opinion_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    emit(
        event_callback,
        DiscussionEvent(
            event_type="round_started",
            round_index=state.current_round,
            payload={"round": state.current_round + 1},
        ),
    )
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
                payload={"comments": opinion.comments, "suggested_changes_summary": opinion.suggested_changes_summary},
            ),
        )
    state.expert_opinions.extend(opinions)
    return state


def objections_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    objections: List[ExpertObjection] = []
    for opinion in state.expert_opinions[-len(ALL_EXPERTS) :]:
        severity = "major" if "安全" in opinion.comments else "minor"
        objection = ExpertObjection(
            from_expert=CHAIR.name,
            to_expert=opinion.expert_name,
            round_index=state.current_round,
            reason="检查营养/安全/时间约束一致性",
            severity=severity,
            target_stance=None,
        )
        objections.append(objection)
        emit(
            event_callback,
            DiscussionEvent(
                event_type="expert_objection",
                round_index=state.current_round,
                expert_name=CHAIR.name,
                target_expert=opinion.expert_name,
                payload={"reason": objection.reason, "severity": severity},
            ),
        )
    state.expert_objections.extend(objections)
    return state


def objection_responses_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    # 简化：所有异议都被接受并反映在步骤提示中
    for objection in state.expert_objections[-len(ALL_EXPERTS) :]:
        objection.target_stance = "accepted"
        objection.target_response = "调整步骤并记录提示"
        objection.resolution = "主席确认并合并"
        emit(
            event_callback,
            DiscussionEvent(
                event_type="objection_response",
                round_index=state.current_round,
                expert_name=objection.to_expert,
                target_expert=objection.from_expert,
                payload={"response": objection.target_response},
            ),
        )
    return state


def chair_decision_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    # 合并最新一轮意见为当前步骤
    if state.expert_opinions:
        last_round_opinions = state.expert_opinions[-len(ALL_EXPERTS) :]
        merged_steps: List[CookingStep] = list(state.current_steps)
        for op in last_round_opinions:
            if op.updated_steps:
                merged_steps = [
                    step.copy(update={"tips": f"{step.tips or ''} | {op.role}: {op.comments[:30]}"})
                    for step in op.updated_steps
                ]
        state.current_steps = merged_steps
    state.current_round += 1
    state.should_stop = state.current_round >= state.max_review_rounds
    emit(
        event_callback,
        DiscussionEvent(
            event_type="chair_decision",
            round_index=state.current_round,
            expert_name=CHAIR.name,
            payload={"should_stop": state.should_stop, "round": state.current_round},
        ),
    )
    return state


def output_formatter_node(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    state.final_recipe = state.final_recipe or _build_full_recipe(state)
    emit(
        event_callback,
        DiscussionEvent(
            event_type="final_summary",
            payload={
                "dish": state.final_recipe.dish.name if state.final_recipe else "",
                "rounds_used": state.current_round,
            },
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
        tutorial_markdown="\n".join([f"### 第{i+1}步: {s.title}\n{s.description}" for i, s in enumerate(state.current_steps)]),
    )

