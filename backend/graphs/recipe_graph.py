"""Simplified LangGraph-style runner placeholder.
This module wires the expert committee nodes in the intended order.
"""
from typing import Callable
from backend.models import OrchestratorState, DiscussionEvent
from backend.agents import nodes

EventCallback = Callable[[DiscussionEvent], None]


def run(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    state = nodes.request_normalizer_node(state, event_callback)
    state = nodes.base_planner_node(state, event_callback)
    while not state.should_stop:
        state = nodes.expert_opinion_node(state, event_callback)
        state = nodes.objections_node(state, event_callback)
        state = nodes.chair_decision_node(state, event_callback)
        if state.current_round >= state.max_review_rounds:
            break
    state = nodes.output_formatter_node(state, event_callback)
    return state


async def astream(state: OrchestratorState, event_callback: EventCallback | None = None) -> OrchestratorState:
    # In a real LangGraph implementation this would be asynchronous; here we reuse sync for brevity.
    return run(state, event_callback)

