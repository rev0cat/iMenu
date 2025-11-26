package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier

@Composable
fun DiscussionScreen() {
    val items = remember { mutableStateListOf("planning_started", "expert_opinion", "final_summary") }
    Column {
        Text(text = "Live discussion (mock)")
        LazyColumn {
            items(items) { item ->
                Card(modifier = Modifier) { Text(text = item) }
            }
        }
    }
}
