from langgraph.graph import END, StateGraph
from backend import models
from backend.agents import followup_nodes


def build_followup_graph() -> StateGraph:
    graph = StateGraph(models.FollowUpState)
    graph.add_node("context", followup_nodes.load_context_node)
    graph.add_node("expert", followup_nodes.followup_expert_node)
    graph.add_node("output", followup_nodes.followup_output_node)
    graph.set_entry_point("context")
    graph.add_edge("context", "expert")
    graph.add_edge("expert", "output")
    graph.add_edge("output", END)
    return graph


followup_graph = build_followup_graph().compile()
