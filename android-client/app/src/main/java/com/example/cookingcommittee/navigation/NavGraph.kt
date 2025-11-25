package com.example.cookingcommittee.navigation

/**
 * Navigation routes for the app.
 */
sealed class Screen(val route: String) {
    object Auth : Screen("auth")
    object Input : Screen("input")
    object Discussion : Screen("discussion")
    object Result : Screen("result")
    object HistoryList : Screen("history_list")
    object HistoryDetail : Screen("history_detail/{sessionId}") {
        fun createRoute(sessionId: Int) = "history_detail/$sessionId"
    }
    object FollowUpDiscussion : Screen("followup_discussion/{sessionId}") {
        fun createRoute(sessionId: Int) = "followup_discussion/$sessionId"
    }
}
