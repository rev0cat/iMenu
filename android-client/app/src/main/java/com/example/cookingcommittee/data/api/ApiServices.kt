package com.example.cookingcommittee.data.api

import com.example.cookingcommittee.data.model.CookingRequestDto
import com.example.cookingcommittee.data.model.DiscussionEventDto
import kotlinx.serialization.Serializable
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path

private const val BASE_URL = "http://10.0.2.2:8000"

interface AuthApiService {
    @POST("/auth/login")
    suspend fun login(@Body request: LoginRequest): TokenResponse

    @POST("/auth/register")
    suspend fun register(@Body request: RegisterRequest): TokenResponse
}

interface RecipeApiService {
    @POST("/generate_recipe")
    suspend fun generateRecipe(
        @Header("Authorization") bearer: String,
        @Body request: CookingRequestDto
    ): FullRecipeResponse

    @GET("/history")
    suspend fun history(@Header("Authorization") bearer: String): List<SessionSummaryDto>

    @POST("/history/{id}/follow_up")
    suspend fun followUp(
        @Header("Authorization") bearer: String,
        @Path("id") id: Int,
        @Body request: FollowUpRequestDto
    ): FollowUpResponseDto
}

interface RecipeWebSocketClient {
    fun open(token: String, onEvent: (DiscussionEventDto) -> Unit)
}

@Serializable
data class RegisterRequest(val email: String, val password: String)

@Serializable
data class LoginRequest(val email: String, val password: String)

@Serializable
data class TokenResponse(val access_token: String, val token_type: String = "bearer")

@Serializable
data class SessionSummaryDto(val id: Int, val created_at: String, val rounds_used: Int, val dish_name: String? = null)

@Serializable
data class FollowUpRequestDto(val session_id: Int, val question: String, val max_review_rounds: Int? = 1)

@Serializable
data class FollowUpResponseDto(val answer: String)

@Serializable
data class FullRecipeResponse(val dish: Map<String, String?>)
