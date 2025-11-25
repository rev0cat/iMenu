package com.example.cookingcommittee.ui.state

import com.example.cookingcommittee.data.model.SessionDetailDto
import com.example.cookingcommittee.data.model.SessionSummaryDto

/**
 * History list UI state.
 */
data class HistoryListUiState(
    val isLoading: Boolean = false,
    val sessions: List<SessionSummaryDto> = emptyList(),
    val error: String? = null
)

/**
 * History detail UI state.
 */
data class HistoryDetailUiState(
    val isLoading: Boolean = false,
    val sessionDetail: SessionDetailDto? = null,
    val followUpQuestion: String = "",
    val isFollowUpLoading: Boolean = false,
    val followUpAnswer: String? = null,
    val error: String? = null
)
