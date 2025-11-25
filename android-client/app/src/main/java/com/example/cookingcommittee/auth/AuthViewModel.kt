package com.example.cookingcommittee.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.cookingcommittee.domain.AuthRepository
import com.example.cookingcommittee.ui.state.AuthUiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * ViewModel for authentication operations.
 */
class AuthViewModel(private val repository: AuthRepository) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()
    
    init {
        checkLoginStatus()
    }
    
    private fun checkLoginStatus() {
        viewModelScope.launch {
            val isLoggedIn = repository.isLoggedIn()
            _uiState.update { it.copy(isLoggedIn = isLoggedIn) }
        }
    }
    
    fun updateEmail(email: String) {
        _uiState.update { it.copy(email = email, error = null) }
    }
    
    fun updatePassword(password: String) {
        _uiState.update { it.copy(password = password, error = null) }
    }
    
    fun toggleRegisterMode() {
        _uiState.update { it.copy(isRegisterMode = !it.isRegisterMode, error = null) }
    }
    
    fun submit() {
        val state = _uiState.value
        
        if (state.email.isBlank() || state.password.isBlank()) {
            _uiState.update { it.copy(error = "请填写邮箱和密码") }
            return
        }
        
        _uiState.update { it.copy(isLoading = true, error = null) }
        
        viewModelScope.launch {
            val result = if (state.isRegisterMode) {
                repository.register(state.email, state.password)
            } else {
                repository.login(state.email, state.password)
            }
            
            result.fold(
                onSuccess = {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            isLoggedIn = true,
                            email = "",
                            password = ""
                        )
                    }
                },
                onFailure = { e ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = e.message ?: "操作失败"
                        )
                    }
                }
            )
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            repository.logout()
            _uiState.update {
                AuthUiState(isLoggedIn = false)
            }
        }
    }
    
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
    
    companion object {
        fun factory(repository: AuthRepository): ViewModelProvider.Factory {
            return object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T {
                    return AuthViewModel(repository) as T
                }
            }
        }
    }
}
