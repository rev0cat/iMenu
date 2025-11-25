package com.example.cookingcommittee

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.cookingcommittee.auth.AuthScreen
import com.example.cookingcommittee.auth.AuthViewModel
import com.example.cookingcommittee.data.model.*
import com.example.cookingcommittee.domain.AuthRepository
import com.example.cookingcommittee.domain.HistoryRepository
import com.example.cookingcommittee.domain.RecipeRepository
import com.example.cookingcommittee.navigation.Screen
import com.example.cookingcommittee.ui.screen.*
import com.example.cookingcommittee.ui.state.*
import com.example.cookingcommittee.ui.theme.CookingCommitteeTheme
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.util.UUID

class MainActivity : ComponentActivity() {
    
    private lateinit var authRepository: AuthRepository
    private lateinit var recipeRepository: RecipeRepository
    private lateinit var historyRepository: HistoryRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize repositories
        authRepository = AuthRepository(applicationContext)
        recipeRepository = RecipeRepository(authRepository)
        historyRepository = HistoryRepository(authRepository)
        
        setContent {
            CookingCommitteeTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    CookingCommitteeApp(
                        authRepository = authRepository,
                        recipeRepository = recipeRepository,
                        historyRepository = historyRepository
                    )
                }
            }
        }
    }
}

@Composable
fun CookingCommitteeApp(
    authRepository: AuthRepository,
    recipeRepository: RecipeRepository,
    historyRepository: HistoryRepository
) {
    val navController = rememberNavController()
    val coroutineScope = rememberCoroutineScope()
    
    // Auth ViewModel
    val authViewModel: AuthViewModel = viewModel(
        factory = AuthViewModel.factory(authRepository)
    )
    val authUiState by authViewModel.uiState.collectAsState()
    
    // Recipe state
    var recipeUiState by remember { mutableStateOf(RecipeUiState()) }
    
    // Discussion state
    var discussionUiState by remember { mutableStateOf(DiscussionUiState()) }
    
    // History state
    var historyListUiState by remember { mutableStateOf(HistoryListUiState()) }
    var historyDetailUiState by remember { mutableStateOf(HistoryDetailUiState()) }
    
    // Current session for result viewing
    var currentRecipe by remember { mutableStateOf<FullRecipeDto?>(null) }
    var currentSessionId by remember { mutableStateOf<Int?>(null) }
    
    // Helper to build CookingRequestDto from UI state
    fun buildCookingRequest(): CookingRequestDto {
        return CookingRequestDto(
            ingredients = recipeUiState.ingredients
                .filter { it.name.isNotBlank() }
                .map { ing ->
                    IngredientInputDto(
                        name = ing.name,
                        state = ing.state.ifBlank { "raw" },
                        amount = ing.amount.toFloatOrNull(),
                        unit = ing.unit.ifBlank { null },
                        notes = ing.notes.ifBlank { null }
                    )
                },
            tools = recipeUiState.tools
                .filter { it.name.isNotBlank() }
                .map { tool ->
                    ToolInputDto(
                        name = tool.name,
                        type = tool.type.ifBlank { null }
                    )
                },
            constraints = ConstraintsDto(
                goal = recipeUiState.constraints.goal.ifBlank { null },
                timeLimitMin = recipeUiState.constraints.timeLimitMin.toIntOrNull(),
                difficulty = recipeUiState.constraints.difficulty.ifBlank { null },
                dietaryRestrictions = recipeUiState.constraints.dietaryRestrictions
                    .split(",")
                    .map { it.trim() }
                    .filter { it.isNotBlank() }
                    .ifEmpty { null }
            ),
            userNotes = recipeUiState.userNotes.ifBlank { null },
            maxReviewRounds = recipeUiState.maxReviewRounds
        )
    }
    
    // Helper to convert DiscussionEventDto to UI model
    fun DiscussionEventDto.toUiModel(): DiscussionItemUi {
        val text = when (eventType) {
            "planning_started" -> "开始规划菜谱..."
            "initial_plan" -> {
                val dishName = payload["dish_plan"]?.jsonObject?.get("name")?.jsonPrimitive?.content
                "初始方案: $dishName"
            }
            "round_started" -> "第 $roundIndex 轮评审开始"
            "expert_opinion" -> {
                val opinion = payload["opinion"]?.jsonObject
                val comments = opinion?.get("comments")?.jsonPrimitive?.content ?: ""
                comments.take(200) + if (comments.length > 200) "..." else ""
            }
            "expert_objection" -> {
                val objection = payload["objection"]?.jsonObject
                val reason = objection?.get("reason")?.jsonPrimitive?.content ?: "提出异议"
                "异议: $reason"
            }
            "objection_response" -> {
                val stance = payload["stance"]?.jsonPrimitive?.content
                val response = payload["response"]?.jsonPrimitive?.content ?: ""
                val stanceText = if (stance == "accepted") "接受" else "反驳"
                "$stanceText: ${response.take(100)}"
            }
            "chair_decision" -> {
                val decision = payload["decision"]?.jsonPrimitive?.content ?: "主席作出裁决"
                decision.take(200)
            }
            "round_finished" -> "第 $roundIndex 轮评审结束"
            "final_summary" -> {
                val dishName = payload["dish_name"]?.jsonPrimitive?.content
                "会议结束，最终菜品: $dishName"
            }
            "followup_question" -> {
                val question = payload["question"]?.jsonPrimitive?.content ?: ""
                "追问: $question"
            }
            "followup_answer" -> {
                val answer = payload["answer"]?.jsonPrimitive?.content ?: ""
                "回答: ${answer.take(200)}"
            }
            "complete" -> "处理完成"
            else -> error ?: eventType
        }
        
        return DiscussionItemUi(
            id = UUID.randomUUID().toString(),
            type = eventType.toDiscussionType(),
            roundIndex = roundIndex,
            expertName = expertName,
            targetExpert = targetExpert,
            text = text,
            isPartial = partial
        )
    }
    
    // Determine start destination based on login state
    val startDestination = if (authUiState.isLoggedIn) Screen.Input.route else Screen.Auth.route
    
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // Auth screen
        composable(Screen.Auth.route) {
            LaunchedEffect(authUiState.isLoggedIn) {
                if (authUiState.isLoggedIn) {
                    navController.navigate(Screen.Input.route) {
                        popUpTo(Screen.Auth.route) { inclusive = true }
                    }
                }
            }
            
            AuthScreen(
                uiState = authUiState,
                onEmailChange = authViewModel::updateEmail,
                onPasswordChange = authViewModel::updatePassword,
                onToggleMode = authViewModel::toggleRegisterMode,
                onSubmit = authViewModel::submit,
                onDismissError = authViewModel::clearError
            )
        }
        
        // Input screen
        composable(Screen.Input.route) {
            InputScreen(
                uiState = recipeUiState,
                onIngredientsChange = { recipeUiState = recipeUiState.copy(ingredients = it) },
                onToolsChange = { recipeUiState = recipeUiState.copy(tools = it) },
                onConstraintsChange = { recipeUiState = recipeUiState.copy(constraints = it) },
                onUserNotesChange = { recipeUiState = recipeUiState.copy(userNotes = it) },
                onMaxRoundsChange = { recipeUiState = recipeUiState.copy(maxReviewRounds = it) },
                onGenerateRecipe = {
                    coroutineScope.launch {
                        recipeUiState = recipeUiState.copy(isLoading = true, error = null)
                        val request = buildCookingRequest()
                        recipeRepository.generateRecipe(request).fold(
                            onSuccess = { recipe ->
                                recipeUiState = recipeUiState.copy(isLoading = false, result = recipe)
                                currentRecipe = recipe
                                navController.navigate(Screen.Result.route)
                            },
                            onFailure = { e ->
                                recipeUiState = recipeUiState.copy(
                                    isLoading = false,
                                    error = e.message ?: "生成失败"
                                )
                            }
                        )
                    }
                },
                onExpertMeeting = {
                    coroutineScope.launch {
                        discussionUiState = DiscussionUiState(isLoading = true, isConnected = true)
                        val request = buildCookingRequest()
                        navController.navigate(Screen.Discussion.route)
                        
                        try {
                            recipeRepository.generateRecipeStream(request)
                                .catch { e ->
                                    discussionUiState = discussionUiState.copy(
                                        error = e.message ?: "连接失败",
                                        isLoading = false
                                    )
                                }
                                .collect { event ->
                                    val uiEvent = event.toUiModel()
                                    discussionUiState = discussionUiState.copy(
                                        events = discussionUiState.events + uiEvent,
                                        currentRound = event.roundIndex ?: discussionUiState.currentRound,
                                        isLoading = event.eventType != "complete",
                                        isComplete = event.eventType == "complete",
                                        error = event.error
                                    )
                                    
                                    // Extract final recipe from complete event
                                    if (event.eventType == "complete") {
                                        val recipeJson = event.payload["recipe"]?.jsonObject
                                        // Note: In a real app, we'd parse this properly
                                        discussionUiState = discussionUiState.copy(
                                            isComplete = true,
                                            isLoading = false
                                        )
                                    }
                                }
                        } catch (e: Exception) {
                            discussionUiState = discussionUiState.copy(
                                error = e.message ?: "处理失败",
                                isLoading = false
                            )
                        }
                    }
                },
                onNavigateToHistory = {
                    coroutineScope.launch {
                        historyListUiState = historyListUiState.copy(isLoading = true, error = null)
                        historyRepository.getHistory().fold(
                            onSuccess = { sessions ->
                                historyListUiState = historyListUiState.copy(
                                    isLoading = false,
                                    sessions = sessions
                                )
                            },
                            onFailure = { e ->
                                historyListUiState = historyListUiState.copy(
                                    isLoading = false,
                                    error = e.message ?: "加载失败"
                                )
                            }
                        )
                    }
                    navController.navigate(Screen.HistoryList.route)
                },
                onLogout = {
                    authViewModel.logout()
                    navController.navigate(Screen.Auth.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        
        // Discussion screen
        composable(Screen.Discussion.route) {
            DiscussionScreen(
                uiState = discussionUiState,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onViewResult = {
                    if (discussionUiState.finalRecipe != null) {
                        currentRecipe = discussionUiState.finalRecipe
                        navController.navigate(Screen.Result.route)
                    }
                }
            )
        }
        
        // Result screen
        composable(Screen.Result.route) {
            ResultScreen(
                recipe = currentRecipe,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToHome = {
                    navController.navigate(Screen.Input.route) {
                        popUpTo(Screen.Input.route) { inclusive = true }
                    }
                }
            )
        }
        
        // History list screen
        composable(Screen.HistoryList.route) {
            HistoryListScreen(
                uiState = historyListUiState,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onSessionClick = { sessionId ->
                    currentSessionId = sessionId
                    coroutineScope.launch {
                        historyDetailUiState = HistoryDetailUiState(isLoading = true)
                        historyRepository.getSessionDetail(sessionId).fold(
                            onSuccess = { detail ->
                                historyDetailUiState = historyDetailUiState.copy(
                                    isLoading = false,
                                    sessionDetail = detail
                                )
                            },
                            onFailure = { e ->
                                historyDetailUiState = historyDetailUiState.copy(
                                    isLoading = false,
                                    error = e.message ?: "加载失败"
                                )
                            }
                        )
                    }
                    navController.navigate(Screen.HistoryDetail.createRoute(sessionId))
                },
                onRefresh = {
                    coroutineScope.launch {
                        historyListUiState = historyListUiState.copy(isLoading = true, error = null)
                        historyRepository.getHistory().fold(
                            onSuccess = { sessions ->
                                historyListUiState = historyListUiState.copy(
                                    isLoading = false,
                                    sessions = sessions
                                )
                            },
                            onFailure = { e ->
                                historyListUiState = historyListUiState.copy(
                                    isLoading = false,
                                    error = e.message ?: "加载失败"
                                )
                            }
                        )
                    }
                }
            )
        }
        
        // History detail screen
        composable(
            route = Screen.HistoryDetail.route,
            arguments = listOf(navArgument("sessionId") { type = NavType.IntType })
        ) { backStackEntry ->
            val sessionId = backStackEntry.arguments?.getInt("sessionId") ?: return@composable
            
            HistoryDetailScreen(
                uiState = historyDetailUiState,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onFollowUpQuestionChange = { question ->
                    historyDetailUiState = historyDetailUiState.copy(followUpQuestion = question)
                },
                onSubmitFollowUp = {
                    coroutineScope.launch {
                        historyDetailUiState = historyDetailUiState.copy(
                            isFollowUpLoading = true,
                            error = null
                        )
                        historyRepository.followUp(
                            sessionId = sessionId,
                            question = historyDetailUiState.followUpQuestion
                        ).fold(
                            onSuccess = { response ->
                                historyDetailUiState = historyDetailUiState.copy(
                                    isFollowUpLoading = false,
                                    followUpAnswer = response.answer,
                                    followUpQuestion = ""
                                )
                            },
                            onFailure = { e ->
                                historyDetailUiState = historyDetailUiState.copy(
                                    isFollowUpLoading = false,
                                    error = e.message ?: "追问失败"
                                )
                            }
                        )
                    }
                },
                onSubmitFollowUpStream = {
                    coroutineScope.launch {
                        discussionUiState = DiscussionUiState(isLoading = true, isConnected = true)
                        navController.navigate(Screen.FollowUpDiscussion.createRoute(sessionId))
                        
                        try {
                            historyRepository.followUpStream(
                                sessionId = sessionId,
                                question = historyDetailUiState.followUpQuestion
                            ).catch { e ->
                                discussionUiState = discussionUiState.copy(
                                    error = e.message ?: "连接失败",
                                    isLoading = false
                                )
                            }.collect { event ->
                                val uiEvent = event.toUiModel()
                                discussionUiState = discussionUiState.copy(
                                    events = discussionUiState.events + uiEvent,
                                    currentRound = event.roundIndex ?: discussionUiState.currentRound,
                                    isLoading = event.eventType != "complete",
                                    isComplete = event.eventType == "complete",
                                    error = event.error
                                )
                            }
                        } catch (e: Exception) {
                            discussionUiState = discussionUiState.copy(
                                error = e.message ?: "处理失败",
                                isLoading = false
                            )
                        }
                    }
                }
            )
        }
        
        // Follow-up discussion screen
        composable(
            route = Screen.FollowUpDiscussion.route,
            arguments = listOf(navArgument("sessionId") { type = NavType.IntType })
        ) {
            DiscussionScreen(
                uiState = discussionUiState,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onViewResult = {
                    // Navigate back to detail
                    navController.popBackStack()
                }
            )
        }
    }
}
