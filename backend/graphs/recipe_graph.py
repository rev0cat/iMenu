"""
LangGraph definition for the recipe generation workflow.
"""
from typing import Any, Callable, Dict, List, Optional, Literal
from langgraph.graph import StateGraph, END

from state import OrchestratorState
from models import CookingRequest, FullRecipe, DiscussionEvent
from agents.nodes import (
    request_normalizer_node,
    base_planner_node,
    chef_opinion_node,
    nutrition_opinion_node,
    tool_process_opinion_node,
    newbie_opinion_node,
    safety_opinion_node,
    objections_node,
    objection_responses_node,
    chair_decision_node,
    output_formatter_node,
)


def should_continue_review(state: OrchestratorState) -> Literal["continue", "finish"]:
    """
    Conditional edge: determine if we should continue to another review round.
    """
    if state.should_stop:
        return "finish"
    if state.current_round > state.max_review_rounds:
        return "finish"
    return "continue"


def create_recipe_graph() -> StateGraph:
    """
    Create the LangGraph for recipe generation.
    
    Flow:
    1. request_normalizer -> base_planner
    2. base_planner -> expert_opinions (parallel)
    3. expert_opinions -> objections
    4. objections -> objection_responses
    5. objection_responses -> chair_decision
    6. chair_decision -> (conditional) either back to expert_opinions or output_formatter
    7. output_formatter -> END
    """
    # Define the graph with OrchestratorState
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes
    workflow.add_node("request_normalizer", request_normalizer_node)
    workflow.add_node("base_planner", base_planner_node)
    workflow.add_node("chef_opinion", chef_opinion_node)
    workflow.add_node("nutrition_opinion", nutrition_opinion_node)
    workflow.add_node("tool_process_opinion", tool_process_opinion_node)
    workflow.add_node("newbie_opinion", newbie_opinion_node)
    workflow.add_node("safety_opinion", safety_opinion_node)
    workflow.add_node("objections", objections_node)
    workflow.add_node("objection_responses", objection_responses_node)
    workflow.add_node("chair_decision", chair_decision_node)
    workflow.add_node("output_formatter", output_formatter_node)
    
    # Set entry point
    workflow.set_entry_point("request_normalizer")
    
    # Define edges
    workflow.add_edge("request_normalizer", "base_planner")
    
    # After base planner, go to expert opinions (in sequence for simplicity)
    # In a more advanced setup, these could run in parallel
    workflow.add_edge("base_planner", "chef_opinion")
    workflow.add_edge("chef_opinion", "nutrition_opinion")
    workflow.add_edge("nutrition_opinion", "tool_process_opinion")
    workflow.add_edge("tool_process_opinion", "newbie_opinion")
    workflow.add_edge("newbie_opinion", "safety_opinion")
    workflow.add_edge("safety_opinion", "objections")
    
    # Objection handling
    workflow.add_edge("objections", "objection_responses")
    workflow.add_edge("objection_responses", "chair_decision")
    
    # Conditional edge from chair_decision
    workflow.add_conditional_edges(
        "chair_decision",
        should_continue_review,
        {
            "continue": "chef_opinion",  # Another round of reviews
            "finish": "output_formatter"
        }
    )
    
    # Output formatter leads to end
    workflow.add_edge("output_formatter", END)
    
    return workflow


def run_recipe_graph(
    request: CookingRequest,
    user_id: Optional[int] = None
) -> OrchestratorState:
    """
    Run the recipe generation graph synchronously.
    
    Args:
        request: The cooking request from the user.
        user_id: Optional user ID for database operations.
        
    Returns:
        Final OrchestratorState with the generated recipe.
    """
    # Create initial state
    initial_state = OrchestratorState(
        request=request,
        user_id=user_id
    )
    
    # Create and compile the graph
    workflow = create_recipe_graph()
    app = workflow.compile()
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    return final_state


def run_recipe_graph_stream(
    request: CookingRequest,
    event_callback: Callable[[DiscussionEvent], None],
    user_id: Optional[int] = None
) -> OrchestratorState:
    """
    Run the recipe generation graph with streaming events.
    
    Args:
        request: The cooking request from the user.
        event_callback: Callback function to receive streaming events.
        user_id: Optional user ID for database operations.
        
    Returns:
        Final OrchestratorState with the generated recipe.
    """
    # Create initial state
    initial_state = OrchestratorState(
        request=request,
        user_id=user_id
    )
    
    # Create and compile the graph
    workflow = create_recipe_graph()
    app = workflow.compile()
    
    # Track seen events to avoid duplicates
    seen_event_ids = set()
    final_state = None
    
    # Stream through the graph
    for state_update in app.stream(initial_state):
        # Get the latest state from the update
        for node_name, node_output in state_update.items():
            if isinstance(node_output, dict):
                # Check for new events
                events = node_output.get("events", [])
                for event in events:
                    event_id = f"{event.event_type}_{event.round_index}_{event.expert_name}_{event.timestamp}"
                    if event_id not in seen_event_ids:
                        seen_event_ids.add(event_id)
                        event_callback(event)
            elif isinstance(node_output, OrchestratorState):
                final_state = node_output
                # Send any new events from state
                for event in node_output.events:
                    event_id = f"{event.event_type}_{event.round_index}_{event.expert_name}_{event.timestamp}"
                    if event_id not in seen_event_ids:
                        seen_event_ids.add(event_id)
                        event_callback(event)
    
    # Get final state if not captured
    if final_state is None:
        final_state = app.invoke(initial_state)
    
    return final_state
