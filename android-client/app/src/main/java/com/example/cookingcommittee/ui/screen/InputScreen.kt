package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
fun InputScreen(onShowResult: () -> Unit, onStartStream: () -> Unit) {
    val ingredient = remember { mutableStateOf("") }
    val goal = remember { mutableStateOf("") }
    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(text = "Compose request")
        OutlinedTextField(value = ingredient.value, onValueChange = { ingredient.value = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Ingredient") })
        OutlinedTextField(value = goal.value, onValueChange = { goal.value = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Goal / Constraints") })
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onShowResult) { Text("Generate (HTTP)") }
            Button(onClick = onStartStream) { Text("Stream discussion") }
        }
    }
}
