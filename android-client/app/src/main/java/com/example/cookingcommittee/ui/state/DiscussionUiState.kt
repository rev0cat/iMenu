package com.example.cookingcommittee.ui.state

import com.example.cookingcommittee.data.model.DiscussionItemUi
import com.example.cookingcommittee.data.model.FullRecipeDto

/**
 * Discussion screen UI state.
 */
data class DiscussionUiState(
    val isLoading: Boolean = false,
    val isConnected: Boolean = false,
    val events: List<DiscussionItemUi> = emptyList(),
    val currentRound: Int = 0,
    val finalRecipe: FullRecipeDto? = null,
    val error: String? = null,
    val isComplete: Boolean = false
)
