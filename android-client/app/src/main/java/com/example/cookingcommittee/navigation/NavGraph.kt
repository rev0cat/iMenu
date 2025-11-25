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

sealed class Destinations(val route: String) {
    data object Auth : Destinations("auth")
    data object Input : Destinations("input")
    data object Result : Destinations("result")
    data object Discussion : Destinations("discussion")
}

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Destinations.Auth.route) {
        composable(Destinations.Auth.route) { AuthScreen(onLoggedIn = { navController.navigate(Destinations.Input.route) }) }
        composable(Destinations.Input.route) {
            InputScreen(
                onShowResult = { navController.navigate(Destinations.Result.route) },
                onShowDiscussion = { navController.navigate(Destinations.Discussion.route) }
            )
        }
        composable(Destinations.Result.route) { ResultScreen() }
        composable(Destinations.Discussion.route) { DiscussionScreen() }
    }
}
