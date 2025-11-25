package com.example.cookingcommittee.data.model

import kotlinx.serialization.Serializable

@Serializable
data class DishPlanDto(
    val name: String,
    val cuisine: String? = null,
    val rationale: String,
    val high_level_steps: List<String>,
)

@Serializable
data class CookingStepDto(
    val index: Int,
    val title: String,
    val description: String,
    val actions: List<String>,
    val tools_used: List<String>,
    val ingredients_used: List<String>,
    val time_estimate_min: Double? = null,
    val tips: String? = null,
    val safety_notes: String? = null,
)

@Serializable
data class FullRecipeDto(
    val dish: DishPlanDto,
    val steps: List<CookingStepDto>,
    val review_rounds_used: Int,
)
