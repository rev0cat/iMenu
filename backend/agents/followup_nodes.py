from backend import models
from backend.llm.mock_client import get_llm_client


def load_context_node(state: models.FollowUpState) -> models.FollowUpState:
    return state


def followup_expert_node(state: models.FollowUpState) -> models.FollowUpState:
    llm = get_llm_client("mock")
    answer = llm.generate(f"Answer follow-up: {state.question}")
    state.discussion_events.append(
        models.DiscussionEvent(
            event_type="followup_answer",
            payload={"text": answer},
            partial=False,
        )
    )
    state.recipe.tutorial_markdown = (state.recipe.tutorial_markdown or "") + "\nFollow-up handled."
    return state


def followup_output_node(state: models.FollowUpState) -> models.FollowUpResponse:
    return models.FollowUpResponse(answer=state.discussion_events[-1].payload.get("text", ""), updated_recipe=state.recipe)
