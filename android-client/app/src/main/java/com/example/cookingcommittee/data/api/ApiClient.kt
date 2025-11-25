package com.example.cookingcommittee.data.api

import com.example.cookingcommittee.BuildConfig
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import java.util.concurrent.TimeUnit

/**
 * API client singleton for network operations.
 */
object ApiClient {
    
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
        isLenient = true
    }
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()
    
    val authApi: AuthApiService = retrofit.create(AuthApiService::class.java)
    val recipeApi: RecipeApiService = retrofit.create(RecipeApiService::class.java)
    
    /**
     * Get OkHttpClient for WebSocket connections.
     */
    fun getOkHttpClient(): OkHttpClient = okHttpClient
    
    /**
     * Get JSON serializer for WebSocket message parsing.
     */
    fun getJson(): Json = json
}
