from langgraph.graph import END, StateGraph
from backend import models
from backend.agents import nodes


def build_recipe_graph() -> StateGraph:
    graph = StateGraph(models.OrchestratorState)
    graph.add_node("request_normalizer", nodes.request_normalizer_node)
    graph.add_node("base_planner", nodes.base_planner_node)
    graph.add_node("chef", nodes.chef_opinion_node)
    graph.add_node("nutrition", nodes.nutrition_opinion_node)
    graph.add_node("tools", nodes.tool_process_opinion_node)
    graph.add_node("coach", nodes.newbie_opinion_node)
    graph.add_node("safety", nodes.safety_opinion_node)
    graph.add_node("objections", nodes.objections_node)
    graph.add_node("responses", nodes.objection_responses_node)
    graph.add_node("chair", nodes.chair_decision_node)
    graph.add_node("output", nodes.output_formatter_node)

    graph.set_entry_point("request_normalizer")
    graph.add_edge("request_normalizer", "base_planner")
    graph.add_edge("base_planner", "chef")
    graph.add_edge("chef", "nutrition")
    graph.add_edge("nutrition", "tools")
    graph.add_edge("tools", "coach")
    graph.add_edge("coach", "safety")
    graph.add_edge("safety", "objections")
    graph.add_edge("objections", "responses")
    graph.add_edge("responses", "chair")

    def should_continue(state: models.OrchestratorState) -> str:
        if state.should_stop or state.current_round >= state.max_review_rounds:
            return "output"
        return "chef"

    graph.add_conditional_edges("chair", should_continue, {"chef": "chef", "output": "output"})
    graph.add_edge("output", END)
    return graph


recipe_graph = build_recipe_graph().compile()
