package com.example.cookingcommittee.data.api

import com.example.cookingcommittee.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Authentication API service.
 */
interface AuthApiService {
    
    @POST("auth/register")
    suspend fun register(
        @Body request: RegisterRequestDto
    ): Response<TokenResponseDto>
    
    @POST("auth/login")
    suspend fun login(
        @Body request: LoginRequestDto
    ): Response<TokenResponseDto>
}

/**
 * Recipe API service.
 */
interface RecipeApiService {
    
    @POST("generate_recipe")
    suspend fun generateRecipe(
        @Header("Authorization") token: String,
        @Body request: CookingRequestDto
    ): Response<FullRecipeDto>
    
    @GET("history")
    suspend fun getHistory(
        @Header("Authorization") token: String,
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0
    ): Response<List<SessionSummaryDto>>
    
    @GET("history/{session_id}")
    suspend fun getSessionDetail(
        @Header("Authorization") token: String,
        @Path("session_id") sessionId: Int
    ): Response<SessionDetailDto>
    
    @POST("history/{session_id}/follow_up")
    suspend fun followUp(
        @Header("Authorization") token: String,
        @Path("session_id") sessionId: Int,
        @Query("question") question: String,
        @Query("max_review_rounds") maxReviewRounds: Int = 1
    ): Response<FollowUpResponseDto>
}
