package com.example.cookingcommittee.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Ingredient input model for requests.
 */
@Serializable
data class IngredientInputDto(
    val name: String,
    val state: String = "raw",
    val amount: Float? = null,
    val unit: String? = null,
    val notes: String? = null
)

/**
 * Tool input model for requests.
 */
@Serializable
data class ToolInputDto(
    val name: String,
    val type: String? = null
)

/**
 * Cooking constraints.
 */
@Serializable
data class ConstraintsDto(
    val goal: String? = null,
    @SerialName("time_limit_min")
    val timeLimitMin: Int? = null,
    val difficulty: String? = null,
    @SerialName("dietary_restrictions")
    val dietaryRestrictions: List<String>? = null
)

/**
 * Main cooking request DTO.
 */
@Serializable
data class CookingRequestDto(
    val ingredients: List<IngredientInputDto>,
    val tools: List<ToolInputDto> = emptyList(),
    val constraints: ConstraintsDto = ConstraintsDto(),
    @SerialName("user_notes")
    val userNotes: String? = null,
    @SerialName("max_review_rounds")
    val maxReviewRounds: Int = 1
)
