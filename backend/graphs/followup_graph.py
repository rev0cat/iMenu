from typing import Callable
from backend.models import FollowUpState, DiscussionEvent
from backend.agents import followup_nodes

EventCallback = Callable[[DiscussionEvent], None]


def run(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    state = followup_nodes.load_context_node(state, event_callback)
    state = followup_nodes.followup_expert_node(state, event_callback)
    state = followup_nodes.followup_output_node(state, event_callback)
    return state


async def astream(state: FollowUpState, event_callback: EventCallback | None = None) -> FollowUpState:
    return run(state, event_callback)

