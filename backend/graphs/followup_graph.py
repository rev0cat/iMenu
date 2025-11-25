"""
LangGraph definition for the follow-up question workflow.
"""
from typing import Callable, Literal, Optional
from langgraph.graph import StateGraph, END

from state import FollowUpState
from models import CookingRequest, FullRecipe, DiscussionEvent, FollowUpResponse
from agents.followup_nodes import (
    load_context_node,
    followup_chef_node,
    followup_nutrition_node,
    followup_chair_node,
    followup_output_node,
)


def should_continue_followup(state: FollowUpState) -> Literal["continue", "finish"]:
    """
    Conditional edge: determine if follow-up processing should continue.
    """
    if state.should_stop:
        return "finish"
    if state.current_round > state.max_review_rounds:
        return "finish"
    return "continue"


def create_followup_graph() -> StateGraph:
    """
    Create the LangGraph for follow-up question processing.
    
    Flow:
    1. load_context -> chef expert
    2. chef expert -> nutrition expert
    3. nutrition expert -> chair synthesis
    4. chair synthesis -> output
    """
    workflow = StateGraph(FollowUpState)
    
    # Add nodes
    workflow.add_node("load_context", load_context_node)
    workflow.add_node("followup_chef", followup_chef_node)
    workflow.add_node("followup_nutrition", followup_nutrition_node)
    workflow.add_node("followup_chair", followup_chair_node)
    workflow.add_node("followup_output", followup_output_node)
    
    # Set entry point
    workflow.set_entry_point("load_context")
    
    # Define edges
    workflow.add_edge("load_context", "followup_chef")
    workflow.add_edge("followup_chef", "followup_nutrition")
    workflow.add_edge("followup_nutrition", "followup_chair")
    workflow.add_edge("followup_chair", "followup_output")
    workflow.add_edge("followup_output", END)
    
    return workflow


def run_followup_graph(
    session_id: int,
    original_request: CookingRequest,
    original_recipe: FullRecipe,
    question: str,
    max_review_rounds: int = 1,
    user_id: Optional[int] = None
) -> FollowUpState:
    """
    Run the follow-up graph synchronously.
    
    Args:
        session_id: ID of the original session.
        original_request: The original cooking request.
        original_recipe: The original generated recipe.
        question: The follow-up question.
        max_review_rounds: Maximum review rounds.
        user_id: Optional user ID.
        
    Returns:
        Final FollowUpState with the answer.
    """
    initial_state = {
        "session_id": session_id,
        "original_request": original_request,
        "original_recipe": original_recipe,
        "question": question,
        "max_review_rounds": max_review_rounds,
        "current_round": 0,
        "expert_opinions": [],
        "expert_objections": [],
        "answer": None,
        "updated_recipe": None,
        "should_stop": False,
        "events": [],
        "user_id": user_id
    }
    
    workflow = create_followup_graph()
    app = workflow.compile()
    
    result = app.invoke(initial_state)
    
    # Convert to FollowUpState
    final_state = FollowUpState(**result)
    
    return final_state


def run_followup_graph_stream(
    session_id: int,
    original_request: CookingRequest,
    original_recipe: FullRecipe,
    question: str,
    event_callback: Callable[[DiscussionEvent], None],
    max_review_rounds: int = 1,
    user_id: Optional[int] = None
) -> FollowUpState:
    """
    Run the follow-up graph with streaming events.
    
    Args:
        session_id: ID of the original session.
        original_request: The original cooking request.
        original_recipe: The original generated recipe.
        question: The follow-up question.
        event_callback: Callback for streaming events.
        max_review_rounds: Maximum review rounds.
        user_id: Optional user ID.
        
    Returns:
        Final FollowUpState with the answer.
    """
    initial_state = {
        "session_id": session_id,
        "original_request": original_request,
        "original_recipe": original_recipe,
        "question": question,
        "max_review_rounds": max_review_rounds,
        "current_round": 0,
        "expert_opinions": [],
        "expert_objections": [],
        "answer": None,
        "updated_recipe": None,
        "should_stop": False,
        "events": [],
        "user_id": user_id
    }
    
    workflow = create_followup_graph()
    app = workflow.compile()
    
    seen_event_ids = set()
    final_result = None
    
    for state_update in app.stream(initial_state):
        for node_name, node_output in state_update.items():
            if isinstance(node_output, dict):
                events = node_output.get("events", [])
                for event in events:
                    event_id = f"{event.event_type}_{event.round_index}_{event.expert_name}_{event.timestamp}"
                    if event_id not in seen_event_ids:
                        seen_event_ids.add(event_id)
                        event_callback(event)
            final_result = node_output
    
    if final_result is None:
        final_result = app.invoke(initial_state)
    
    # Convert to FollowUpState
    if isinstance(final_result, dict):
        final_state = FollowUpState(**final_result)
    else:
        final_state = final_result
    
    return final_state
