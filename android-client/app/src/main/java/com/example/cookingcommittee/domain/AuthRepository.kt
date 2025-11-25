package com.example.cookingcommittee.domain

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.cookingcommittee.data.api.ApiClient
import com.example.cookingcommittee.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

/**
 * Repository for authentication operations.
 */
class AuthRepository(private val context: Context) {
    
    private val api = ApiClient.authApi
    private val tokenKey = stringPreferencesKey("access_token")
    
    /**
     * Get stored token as Flow.
     */
    val tokenFlow: Flow<String?> = context.dataStore.data.map { prefs ->
        prefs[tokenKey]
    }
    
    /**
     * Get current token synchronously.
     */
    suspend fun getToken(): String? = tokenFlow.first()
    
    /**
     * Get token with Bearer prefix for API calls.
     */
    suspend fun getBearerToken(): String {
        val token = getToken() ?: throw IllegalStateException("Not authenticated")
        return "Bearer $token"
    }
    
    /**
     * Check if user is logged in.
     */
    suspend fun isLoggedIn(): Boolean = getToken() != null
    
    /**
     * Register a new user.
     */
    suspend fun register(email: String, password: String): Result<TokenResponseDto> {
        return try {
            val response = api.register(RegisterRequestDto(email, password))
            if (response.isSuccessful && response.body() != null) {
                val token = response.body()!!
                saveToken(token.accessToken)
                Result.success(token)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "注册失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Login user.
     */
    suspend fun login(email: String, password: String): Result<TokenResponseDto> {
        return try {
            val response = api.login(LoginRequestDto(email, password))
            if (response.isSuccessful && response.body() != null) {
                val token = response.body()!!
                saveToken(token.accessToken)
                Result.success(token)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "登录失败"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Save token to DataStore.
     */
    private suspend fun saveToken(token: String) {
        context.dataStore.edit { prefs ->
            prefs[tokenKey] = token
        }
    }
    
    /**
     * Clear token (logout).
     */
    suspend fun logout() {
        context.dataStore.edit { prefs ->
            prefs.remove(tokenKey)
        }
    }
}
