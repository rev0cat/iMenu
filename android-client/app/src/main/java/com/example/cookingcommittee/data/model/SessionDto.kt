package com.example.cookingcommittee.data.model

import kotlinx.serialization.Serializable

@Serializable
data class SessionDto(
    val id: Int,
    val created_at: String,
    val dish_name: String? = null,
    val rounds_used: Int? = null,
)

@Serializable
data class FollowUpDto(
    val question: String,
    val answer: String,
)
