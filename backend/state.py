from backend import models


class StateFactory:
    @staticmethod
    def new_orchestrator(request: models.CookingRequest) -> models.OrchestratorState:
        ingredients = [models.Ingredient(**ing.dict()) for ing in request.ingredients]
        tools = [models.Tool(**tool.dict()) for tool in request.tools]
        return models.OrchestratorState(
            request=request,
            ingredients=ingredients,
            tools=tools,
            constraints=request.constraints,
            current_steps=[],
            expert_opinions=[],
            expert_objections=[],
            current_round=0,
            max_review_rounds=request.max_review_rounds or 1,
            should_stop=False,
        )

    @staticmethod
    def new_followup(
        request: models.CookingRequest, recipe: models.FullRecipe, question: str, max_rounds: int
    ) -> models.FollowUpState:
        return models.FollowUpState(
            request=request,
            recipe=recipe,
            question=question,
            current_round=0,
            max_review_rounds=max_rounds,
            discussion_events=[],
        )
