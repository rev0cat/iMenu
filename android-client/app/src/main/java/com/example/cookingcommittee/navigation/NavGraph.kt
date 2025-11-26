package com.example.cookingcommittee.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.cookingcommittee.ui.screen.AuthScreen
import com.example.cookingcommittee.ui.screen.InputScreen
import com.example.cookingcommittee.ui.screen.ResultScreen
import com.example.cookingcommittee.ui.screen.DiscussionScreen
import com.example.cookingcommittee.ui.screen.HistoryListScreen

sealed class Dest(val route: String) {
    object Auth : Dest("auth")
    object Input : Dest("input")
    object Result : Dest("result")
    object Discussion : Dest("discussion")
    object History : Dest("history")
}

@Composable
fun NavGraph(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Dest.Auth.route) {
        composable(Dest.Auth.route) { AuthScreen(onAuthenticated = { navController.navigate(Dest.Input.route) }) }
        composable(Dest.Input.route) { InputScreen(onShowResult = { navController.navigate(Dest.Result.route) }, onStartStream = { navController.navigate(Dest.Discussion.route) }) }
        composable(Dest.Result.route) { ResultScreen() }
        composable(Dest.Discussion.route) { DiscussionScreen() }
        composable(Dest.History.route) { HistoryListScreen(onSelect = { navController.navigate(Dest.Result.route) }) }
    }
}
