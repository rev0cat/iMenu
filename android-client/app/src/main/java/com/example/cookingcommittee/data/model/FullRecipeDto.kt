package com.example.cookingcommittee.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Dish plan from the expert committee.
 */
@Serializable
data class DishPlanDto(
    val name: String,
    val cuisine: String? = null,
    val rationale: String,
    @SerialName("high_level_steps")
    val highLevelSteps: List<String>
)

/**
 * Cooking step with details.
 */
@Serializable
data class CookingStepDto(
    val index: Int,
    val title: String,
    val description: String,
    val actions: List<String> = emptyList(),
    @SerialName("tools_used")
    val toolsUsed: List<String> = emptyList(),
    @SerialName("ingredients_used")
    val ingredientsUsed: List<String> = emptyList(),
    @SerialName("time_estimate_min")
    val timeEstimateMin: Float? = null,
    val tips: String? = null,
    @SerialName("safety_notes")
    val safetyNotes: String? = null
)

/**
 * Standardized ingredient.
 */
@Serializable
data class IngredientDto(
    val name: String,
    val state: String,
    val amount: Float? = null,
    val unit: String? = null,
    val notes: String? = null
)

/**
 * Standardized tool.
 */
@Serializable
data class ToolDto(
    val name: String,
    val type: String? = null
)

/**
 * Expert opinion.
 */
@Serializable
data class ExpertOpinionDto(
    @SerialName("expert_name")
    val expertName: String,
    val role: String,
    @SerialName("round_index")
    val roundIndex: Int,
    val comments: String,
    @SerialName("suggested_changes_summary")
    val suggestedChangesSummary: String,
    @SerialName("updated_dish_plan")
    val updatedDishPlan: DishPlanDto? = null,
    @SerialName("updated_steps")
    val updatedSteps: List<CookingStepDto>? = null
)

/**
 * Expert objection.
 */
@Serializable
data class ExpertObjectionDto(
    @SerialName("from_expert")
    val fromExpert: String,
    @SerialName("to_expert")
    val toExpert: String,
    @SerialName("round_index")
    val roundIndex: Int,
    val reason: String,
    val severity: String = "minor",
    @SerialName("target_stance")
    val targetStance: String? = null,
    @SerialName("target_response")
    val targetResponse: String? = null,
    val resolution: String? = null
)

/**
 * Full recipe response.
 */
@Serializable
data class FullRecipeDto(
    val dish: DishPlanDto,
    val ingredients: List<IngredientDto>,
    val tools: List<ToolDto>,
    val constraints: ConstraintsDto,
    val steps: List<CookingStepDto>,
    @SerialName("expert_opinions")
    val expertOpinions: List<ExpertOpinionDto> = emptyList(),
    @SerialName("expert_objections")
    val expertObjections: List<ExpertObjectionDto> = emptyList(),
    @SerialName("review_rounds_used")
    val reviewRoundsUsed: Int,
    @SerialName("tutorial_markdown")
    val tutorialMarkdown: String? = null
)
