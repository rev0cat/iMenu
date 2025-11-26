package com.example.cookingcommittee.data.ws

import com.example.cookingcommittee.data.model.CookingRequestDto
import com.example.cookingcommittee.data.model.DiscussionEventDto
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener

class RecipeWebSocketClient(private val baseUrl: String) {
    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    fun connect(token: String, body: CookingRequestDto, onEvent: (DiscussionEventDto) -> Unit): WebSocket {
        val request = Request.Builder().url("$baseUrl/ws/generate_recipe_stream?token=$token").build()
        val ws = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                runCatching { json.decodeFromString<DiscussionEventDto>(text) }.onSuccess(onEvent)
            }
        })
        ws.send(json.encodeToString(body))
        return ws
    }
}
