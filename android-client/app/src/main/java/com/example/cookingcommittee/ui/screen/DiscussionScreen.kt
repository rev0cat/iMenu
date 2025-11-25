package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
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
    val events = remember { mutableStateListOf("Chair: session starting", "Chef: provide opinion", "Chair: summary") }
    Column(modifier = Modifier.fillMaxSize()) {
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(events) { item ->
                Card { Text(text = item) }
            }
        }
    }
}
