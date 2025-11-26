from functools import partial
from typing import Callable

from langgraph.graph import END, StateGraph

from backend.agents import followup_nodes
from backend.models import DiscussionEvent, FollowUpState

EventCallback = Callable[[DiscussionEvent], None]


def build_graph(event_callback: EventCallback | None = None):
    workflow = StateGraph(FollowUpState)
    workflow.add_node("load_context", partial(followup_nodes.load_context_node, event_callback=event_callback))
    workflow.add_node("followup_expert", partial(followup_nodes.followup_expert_node, event_callback=event_callback))
    workflow.add_node("followup_output", partial(followup_nodes.followup_output_node, event_callback=event_callback))
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "followup_expert")
    workflow.add_edge("followup_expert", "followup_output")
    workflow.add_edge("followup_output", END)
    return workflow.compile()


def run(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    graph = build_graph(event_callback)
    return graph.invoke(state)


async def astream(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    graph = build_graph(event_callback)
    final_state = state
    async for result in graph.astream(state):
        final_state = result
    return final_state

