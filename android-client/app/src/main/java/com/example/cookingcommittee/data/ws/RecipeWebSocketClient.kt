package com.example.cookingcommittee.data.ws

import com.example.cookingcommittee.BuildConfig
import com.example.cookingcommittee.data.api.ApiClient
import com.example.cookingcommittee.data.model.CookingRequestDto
import com.example.cookingcommittee.data.model.DiscussionEventDto
import com.example.cookingcommittee.data.model.FollowUpRequestDto
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.serialization.encodeToString
import okhttp3.*

/**
 * WebSocket client for streaming recipe generation and follow-up discussions.
 */
class RecipeWebSocketClient {
    
    private val client = ApiClient.getOkHttpClient()
    private val json = ApiClient.getJson()
    
    /**
     * Connect to recipe generation WebSocket and stream events.
     * 
     * @param token JWT access token
     * @param request Cooking request
     * @return Flow of discussion events
     */
    fun generateRecipeStream(
        token: String,
        request: CookingRequestDto
    ): Flow<DiscussionEventDto> = callbackFlow {
        val url = "${BuildConfig.BASE_URL_WS}ws/generate_recipe_stream?token=$token"
        val wsRequest = Request.Builder().url(url).build()
        
        val webSocket = client.newWebSocket(wsRequest, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                // Send cooking request
                val requestJson = json.encodeToString(request)
                webSocket.send(requestJson)
            }
            
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val event = json.decodeFromString<DiscussionEventDto>(text)
                    trySend(event)
                    
                    // Close flow on complete or error
                    if (event.eventType == "complete" || event.error != null) {
                        close()
                    }
                } catch (e: Exception) {
                    val errorEvent = DiscussionEventDto(
                        eventType = "error",
                        error = "解析错误: ${e.message}"
                    )
                    trySend(errorEvent)
                }
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                val errorEvent = DiscussionEventDto(
                    eventType = "error",
                    error = "连接失败: ${t.message}"
                )
                trySend(errorEvent)
                close(t)
            }
            
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                close()
            }
        })
        
        awaitClose {
            webSocket.close(1000, "Closed by client")
        }
    }
    
    /**
     * Connect to follow-up WebSocket and stream events.
     * 
     * @param token JWT access token
     * @param sessionId Session ID to follow up on
     * @param question Follow-up question
     * @param maxReviewRounds Max review rounds
     * @return Flow of discussion events
     */
    fun followUpStream(
        token: String,
        sessionId: Int,
        question: String,
        maxReviewRounds: Int = 1
    ): Flow<DiscussionEventDto> = callbackFlow {
        val url = "${BuildConfig.BASE_URL_WS}ws/follow_up_stream?token=$token"
        val wsRequest = Request.Builder().url(url).build()
        
        val webSocket = client.newWebSocket(wsRequest, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                // Send follow-up request
                val requestData = mapOf(
                    "session_id" to sessionId,
                    "question" to question,
                    "max_review_rounds" to maxReviewRounds
                )
                val requestJson = json.encodeToString(requestData)
                webSocket.send(requestJson)
            }
            
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val event = json.decodeFromString<DiscussionEventDto>(text)
                    trySend(event)
                    
                    if (event.eventType == "complete" || event.error != null) {
                        close()
                    }
                } catch (e: Exception) {
                    val errorEvent = DiscussionEventDto(
                        eventType = "error",
                        error = "解析错误: ${e.message}"
                    )
                    trySend(errorEvent)
                }
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                val errorEvent = DiscussionEventDto(
                    eventType = "error",
                    error = "连接失败: ${t.message}"
                )
                trySend(errorEvent)
                close(t)
            }
            
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                close()
            }
        })
        
        awaitClose {
            webSocket.close(1000, "Closed by client")
        }
    }
}
