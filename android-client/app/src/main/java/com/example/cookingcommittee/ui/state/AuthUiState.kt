package com.example.cookingcommittee.ui.state

/**
 * Authentication UI state.
 */
data class AuthUiState(
    val isLoading: Boolean = false,
    val isLoggedIn: Boolean = false,
    val email: String = "",
    val password: String = "",
    val error: String? = null,
    val isRegisterMode: Boolean = false
)
