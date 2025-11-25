package com.example.cookingcommittee.ui.state

import com.example.cookingcommittee.data.model.FullRecipeDto

/**
 * Ingredient input for UI.
 */
data class IngredientInputUi(
    val id: Int = 0,
    val name: String = "",
    val state: String = "raw",
    val amount: String = "",
    val unit: String = "",
    val notes: String = ""
)

/**
 * Tool input for UI.
 */
data class ToolInputUi(
    val id: Int = 0,
    val name: String = "",
    val type: String = ""
)

/**
 * Constraints input for UI.
 */
data class ConstraintsInputUi(
    val goal: String = "",
    val timeLimitMin: String = "",
    val difficulty: String = "",
    val dietaryRestrictions: String = ""
)

/**
 * Recipe generation UI state.
 */
data class RecipeUiState(
    val isLoading: Boolean = false,
    val ingredients: List<IngredientInputUi> = listOf(IngredientInputUi()),
    val tools: List<ToolInputUi> = listOf(ToolInputUi()),
    val constraints: ConstraintsInputUi = ConstraintsInputUi(),
    val userNotes: String = "",
    val maxReviewRounds: Int = 1,
    val result: FullRecipeDto? = null,
    val error: String? = null
)
