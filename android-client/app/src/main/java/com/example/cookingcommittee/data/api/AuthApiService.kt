package com.example.cookingcommittee.data.api

import com.example.cookingcommittee.data.model.CookingRequestDto
import com.example.cookingcommittee.data.model.FullRecipeDto
import com.example.cookingcommittee.data.model.SessionDto
import kotlinx.serialization.Serializable
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path

@Serializable
data class TokenResponseDto(val access_token: String, val token_type: String = "bearer")

interface AuthApiService {
    @POST("/auth/register")
    suspend fun register(@Body body: AuthRequestDto): TokenResponseDto

    @POST("/auth/login")
    suspend fun login(@Body body: AuthRequestDto): TokenResponseDto
}

@Serializable
data class AuthRequestDto(val email: String, val password: String)

interface RecipeApiService {
    @POST("/generate_recipe")
    suspend fun generateRecipe(@Header("Authorization") token: String, @Body body: CookingRequestDto): FullRecipeDto

    @GET("/history")
    suspend fun listHistory(@Header("Authorization") token: String): List<SessionDto>

    @GET("/history/{id}")
    suspend fun sessionDetail(@Header("Authorization") token: String, @Path("id") id: Int): SessionDto
}
