package com.example.cookingcommittee.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

/**
 * Discussion event from WebSocket stream.
 */
@Serializable
data class DiscussionEventDto(
    @SerialName("event_type")
    val eventType: String,
    @SerialName("round_index")
    val roundIndex: Int? = null,
    @SerialName("expert_name")
    val expertName: String? = null,
    @SerialName("target_expert")
    val targetExpert: String? = null,
    val payload: JsonObject = JsonObject(emptyMap()),
    val partial: Boolean = false,
    val timestamp: String? = null,
    val error: String? = null
)

/**
 * UI representation of a discussion event.
 */
data class DiscussionItemUi(
    val id: String,
    val type: DiscussionType,
    val roundIndex: Int?,
    val expertName: String?,
    val targetExpert: String?,
    val text: String,
    val isPartial: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Types of discussion events for UI.
 */
enum class DiscussionType {
    PLANNING_STARTED,
    INITIAL_PLAN,
    ROUND_STARTED,
    EXPERT_OPINION,
    EXPERT_OBJECTION,
    OBJECTION_RESPONSE,
    CHAIR_DECISION,
    ROUND_FINISHED,
    FINAL_SUMMARY,
    FOLLOWUP_QUESTION,
    FOLLOWUP_ANSWER,
    COMPLETE,
    ERROR
}

/**
 * Map event type string to enum.
 */
fun String.toDiscussionType(): DiscussionType = when (this) {
    "planning_started" -> DiscussionType.PLANNING_STARTED
    "initial_plan" -> DiscussionType.INITIAL_PLAN
    "round_started" -> DiscussionType.ROUND_STARTED
    "expert_opinion" -> DiscussionType.EXPERT_OPINION
    "expert_objection" -> DiscussionType.EXPERT_OBJECTION
    "objection_response" -> DiscussionType.OBJECTION_RESPONSE
    "chair_decision" -> DiscussionType.CHAIR_DECISION
    "round_finished" -> DiscussionType.ROUND_FINISHED
    "final_summary" -> DiscussionType.FINAL_SUMMARY
    "followup_question" -> DiscussionType.FOLLOWUP_QUESTION
    "followup_answer" -> DiscussionType.FOLLOWUP_ANSWER
    "complete" -> DiscussionType.COMPLETE
    else -> DiscussionType.ERROR
}
