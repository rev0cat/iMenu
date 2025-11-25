package com.example.cookingcommittee.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Session summary for history list.
 */
@Serializable
data class SessionSummaryDto(
    val id: Int,
    @SerialName("created_at")
    val createdAt: String,
    @SerialName("dish_name")
    val dishName: String? = null,
    val goal: String? = null,
    @SerialName("rounds_used")
    val roundsUsed: Int
)

/**
 * Follow-up summary for session detail.
 */
@Serializable
data class FollowUpSummaryDto(
    val id: Int,
    @SerialName("created_at")
    val createdAt: String,
    val question: String
)

/**
 * Full session detail.
 */
@Serializable
data class SessionDetailDto(
    val id: Int,
    @SerialName("created_at")
    val createdAt: String,
    val request: CookingRequestDto,
    val result: FullRecipeDto,
    val followups: List<FollowUpSummaryDto> = emptyList()
)

/**
 * Follow-up request.
 */
@Serializable
data class FollowUpRequestDto(
    @SerialName("session_id")
    val sessionId: Int,
    val question: String,
    @SerialName("max_review_rounds")
    val maxReviewRounds: Int = 1
)

/**
 * Follow-up response.
 */
@Serializable
data class FollowUpResponseDto(
    val answer: String,
    @SerialName("updated_recipe")
    val updatedRecipe: FullRecipeDto? = null
)
