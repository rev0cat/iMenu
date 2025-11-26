"""LangGraph wiring for专家委员会多轮评审流程."""

from functools import partial
from typing import Callable

from langgraph.graph import END, StateGraph

from backend.agents import nodes
from backend.models import DiscussionEvent, OrchestratorState

EventCallback = Callable[[DiscussionEvent], None]


def build_graph(event_callback: EventCallback | None = None):
    workflow = StateGraph(OrchestratorState)

    workflow.add_node(
        "request_normalizer", partial(nodes.request_normalizer_node, event_callback=event_callback)
    )
    workflow.add_node("base_planner", partial(nodes.base_planner_node, event_callback=event_callback))
    workflow.add_node("expert_opinion", partial(nodes.expert_opinion_node, event_callback=event_callback))
    workflow.add_node("objections", partial(nodes.objections_node, event_callback=event_callback))
    workflow.add_node(
        "objection_responses", partial(nodes.objection_responses_node, event_callback=event_callback)
    )
    workflow.add_node("chair_decision", partial(nodes.chair_decision_node, event_callback=event_callback))
    workflow.add_node("output_formatter", partial(nodes.output_formatter_node, event_callback=event_callback))

    workflow.set_entry_point("request_normalizer")
    workflow.add_edge("request_normalizer", "base_planner")
    workflow.add_edge("base_planner", "expert_opinion")
    workflow.add_edge("expert_opinion", "objections")
    workflow.add_edge("objections", "objection_responses")
    workflow.add_edge("objection_responses", "chair_decision")

    def should_continue(state: OrchestratorState) -> str:
        if not state.should_stop and state.current_round < state.max_review_rounds:
            return "expert_opinion"
        return "output_formatter"

    workflow.add_conditional_edges(
        "chair_decision",
        should_continue,
        {
            "expert_opinion": "expert_opinion",
            "output_formatter": "output_formatter",
        },
    )
    workflow.add_edge("output_formatter", END)
    return workflow.compile()


def run(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    graph = build_graph(event_callback)
    return graph.invoke(state)


async def astream(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    graph = build_graph(event_callback)
    final_state = state
    async for result in graph.astream(state):
        # astream yields intermediate states;我们仅保留最终状态
        final_state = result
    return final_state

