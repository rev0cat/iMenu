package com.example.cookingcommittee.domain

import com.example.cookingcommittee.data.api.ApiClient
import com.example.cookingcommittee.data.model.*
import com.example.cookingcommittee.data.ws.RecipeWebSocketClient
import kotlinx.coroutines.flow.Flow

/**
 * Repository for recipe operations.
 */
class RecipeRepository(private val authRepository: AuthRepository) {
    
    private val api = ApiClient.recipeApi
    private val webSocketClient = RecipeWebSocketClient()
    
    /**
     * Generate recipe synchronously via HTTP.
     */
    suspend fun generateRecipe(request: CookingRequestDto): Result<FullRecipeDto> {
        return try {
            val token = authRepository.getBearerToken()
            val response = api.generateRecipe(token, request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "生成菜谱失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Generate recipe with streaming via WebSocket.
     */
    suspend fun generateRecipeStream(request: CookingRequestDto): Flow<DiscussionEventDto> {
        val token = authRepository.getToken() ?: throw IllegalStateException("Not authenticated")
        return webSocketClient.generateRecipeStream(token, request)
    }
}

/**
 * Repository for history operations.
 */
class HistoryRepository(private val authRepository: AuthRepository) {
    
    private val api = ApiClient.recipeApi
    private val webSocketClient = RecipeWebSocketClient()
    
    /**
     * Get history list.
     */
    suspend fun getHistory(limit: Int = 20, offset: Int = 0): Result<List<SessionSummaryDto>> {
        return try {
            val token = authRepository.getBearerToken()
            val response = api.getHistory(token, limit, offset)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "获取历史失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get session detail.
     */
    suspend fun getSessionDetail(sessionId: Int): Result<SessionDetailDto> {
        return try {
            val token = authRepository.getBearerToken()
            val response = api.getSessionDetail(token, sessionId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "获取详情失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Send follow-up question via HTTP.
     */
    suspend fun followUp(
        sessionId: Int,
        question: String,
        maxReviewRounds: Int = 1
    ): Result<FollowUpResponseDto> {
        return try {
            val token = authRepository.getBearerToken()
            val response = api.followUp(token, sessionId, question, maxReviewRounds)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "追问失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Send follow-up with streaming via WebSocket.
     */
    suspend fun followUpStream(
        sessionId: Int,
        question: String,
        maxReviewRounds: Int = 1
    ): Flow<DiscussionEventDto> {
        val token = authRepository.getToken() ?: throw IllegalStateException("Not authenticated")
        return webSocketClient.followUpStream(token, sessionId, question, maxReviewRounds)
    }
}
