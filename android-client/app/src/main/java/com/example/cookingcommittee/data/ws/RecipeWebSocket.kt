package com.example.cookingcommittee.data.ws

import com.example.cookingcommittee.data.api.RecipeWebSocketClient
import com.example.cookingcommittee.data.model.DiscussionEventDto
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener

class OkHttpRecipeWebSocketClient(private val baseUrl: String = "ws://10.0.2.2:8000") : RecipeWebSocketClient {
    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    override fun open(token: String, onEvent: (DiscussionEventDto) -> Unit) {
        val request = Request.Builder()
            .url("$baseUrl/ws/generate_recipe_stream?token=$token")
            .build()
        client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val event = json.decodeFromString(DiscussionEventDto.serializer(), text)
                onEvent(event)
            }
        })
    }
}
