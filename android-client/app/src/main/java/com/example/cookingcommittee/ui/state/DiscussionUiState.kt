package com.example.cookingcommittee.ui.state

data class DiscussionItemUi(val type: String, val text: String, val roundIndex: Int? = null)

data class DiscussionUiState(
    val items: List<DiscussionItemUi> = emptyList(),
    val isStreaming: Boolean = false,
)
