package com.example.cookingcommittee.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Register request.
 */
@Serializable
data class RegisterRequestDto(
    val email: String,
    val password: String
)

/**
 * Login request.
 */
@Serializable
data class LoginRequestDto(
    val email: String,
    val password: String
)

/**
 * Token response.
 */
@Serializable
data class TokenResponseDto(
    @SerialName("access_token")
    val accessToken: String,
    @SerialName("token_type")
    val tokenType: String = "bearer"
)

/**
 * Error response.
 */
@Serializable
data class ErrorResponseDto(
    val detail: String
)
