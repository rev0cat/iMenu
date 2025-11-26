package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HistoryListScreen(onSelect: (Int) -> Unit) {
    val sessions = remember { mutableStateListOf("Session #1", "Session #2") }
    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "History")
        LazyColumn {
            items(sessions) { session ->
                Card(modifier = Modifier
                    .padding(vertical = 4.dp)
                    .fillMaxWidth()
                    .clickable { onSelect(1) }) {
                    Text(text = session, modifier = Modifier.padding(12.dp))
                }
            }
        }
    }
}
