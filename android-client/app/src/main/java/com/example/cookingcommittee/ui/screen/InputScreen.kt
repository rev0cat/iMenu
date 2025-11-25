package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun InputScreen(onShowResult: () -> Unit, onShowDiscussion: () -> Unit) {
    val notes = remember { mutableStateOf("") }
    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "New Recipe")
        OutlinedTextField(
            value = notes.value,
            onValueChange = { notes.value = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Notes / goal") }
        )
        Button(onClick = onShowResult, modifier = Modifier.padding(top = 12.dp)) {
            Text("Generate via HTTP")
        }
        Button(onClick = onShowDiscussion, modifier = Modifier.padding(top = 12.dp)) {
            Text("Stream via WebSocket")
        }
    }
}
