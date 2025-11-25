package com.example.cookingcommittee

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.cookingcommittee.navigation.NavGraph
import com.example.cookingcommittee.ui.theme.CookingTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CookingTheme {
                NavGraph()
            }
        }
    }
}
