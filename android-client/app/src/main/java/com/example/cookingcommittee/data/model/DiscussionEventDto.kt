package com.example.cookingcommittee.data.model

import kotlinx.serialization.Serializable

@Serializable
data class DiscussionEventDto(
    val event_type: String,
    val round_index: Int? = null,
    val expert_name: String? = null,
    val target_expert: String? = null,
    val payload: Map<String, String?> = emptyMap(),
    val partial: Boolean? = false,
)
