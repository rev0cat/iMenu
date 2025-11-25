package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.Arrangement
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
fun AuthScreen(onAuthenticated: () -> Unit) {
    val email = remember { mutableStateOf("") }
    val password = remember { mutableStateOf("") }
    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(text = "Login / Register")
        OutlinedTextField(value = email.value, onValueChange = { email.value = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Email") })
        OutlinedTextField(value = password.value, onValueChange = { password.value = it }, modifier = Modifier.fillMaxWidth(), label = { Text("Password") })
        Button(onClick = onAuthenticated, modifier = Modifier.fillMaxWidth()) { Text("Continue (mock)") }
    }
}
