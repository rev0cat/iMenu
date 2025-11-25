package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ResultScreen() {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "Recipe Result")
        Text(text = "Dish: Mock Dish")
        Text(text = "Round used: 1")
    }
}
