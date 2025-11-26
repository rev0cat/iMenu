package com.example.cookingcommittee.data.model

import kotlinx.serialization.Serializable

@Serializable
data class IngredientInputDto(
    val name: String,
    val state: String,
    val amount: Double? = null,
    val unit: String? = null,
    val notes: String? = null,
)

@Serializable
data class ToolInputDto(
    val name: String,
    val type: String? = null,
)

@Serializable
data class ConstraintsDto(
    val goal: String? = null,
    val time_limit_min: Int? = null,
    val difficulty: String? = null,
    val dietary_restrictions: List<String>? = null,
)

@Serializable
data class CookingRequestDto(
    val ingredients: List<IngredientInputDto>,
    val tools: List<ToolInputDto>,
    val constraints: ConstraintsDto,
    val user_notes: String? = null,
    val max_review_rounds: Int? = 1,
)
