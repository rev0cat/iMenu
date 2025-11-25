package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.example.cookingcommittee.ui.state.*

/**
 * Input screen for recipe generation.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InputScreen(
    uiState: RecipeUiState,
    onIngredientsChange: (List<IngredientInputUi>) -> Unit,
    onToolsChange: (List<ToolInputUi>) -> Unit,
    onConstraintsChange: (ConstraintsInputUi) -> Unit,
    onUserNotesChange: (String) -> Unit,
    onMaxRoundsChange: (Int) -> Unit,
    onGenerateRecipe: () -> Unit,
    onExpertMeeting: () -> Unit,
    onNavigateToHistory: () -> Unit,
    onLogout: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("新建菜谱") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ),
                actions = {
                    IconButton(onClick = onNavigateToHistory) {
                        Icon(Icons.Default.History, contentDescription = "历史记录")
                    }
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.Logout, contentDescription = "退出登录")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Ingredients section
            SectionTitle(title = "食材", icon = Icons.Default.Restaurant)
            
            uiState.ingredients.forEachIndexed { index, ingredient ->
                IngredientInputCard(
                    ingredient = ingredient,
                    onUpdate = { updated ->
                        val newList = uiState.ingredients.toMutableList()
                        newList[index] = updated
                        onIngredientsChange(newList)
                    },
                    onDelete = {
                        if (uiState.ingredients.size > 1) {
                            val newList = uiState.ingredients.toMutableList()
                            newList.removeAt(index)
                            onIngredientsChange(newList)
                        }
                    }
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            OutlinedButton(
                onClick = {
                    val newList = uiState.ingredients.toMutableList()
                    newList.add(IngredientInputUi(id = newList.size))
                    onIngredientsChange(newList)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.Add, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("添加食材")
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Tools section
            SectionTitle(title = "工具", icon = Icons.Default.Build)
            
            uiState.tools.forEachIndexed { index, tool ->
                ToolInputCard(
                    tool = tool,
                    onUpdate = { updated ->
                        val newList = uiState.tools.toMutableList()
                        newList[index] = updated
                        onToolsChange(newList)
                    },
                    onDelete = {
                        if (uiState.tools.size > 1) {
                            val newList = uiState.tools.toMutableList()
                            newList.removeAt(index)
                            onToolsChange(newList)
                        }
                    }
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            OutlinedButton(
                onClick = {
                    val newList = uiState.tools.toMutableList()
                    newList.add(ToolInputUi(id = newList.size))
                    onToolsChange(newList)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.Add, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("添加工具")
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Constraints section
            SectionTitle(title = "约束条件", icon = Icons.Default.Settings)
            
            ConstraintsInputCard(
                constraints = uiState.constraints,
                onUpdate = onConstraintsChange
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // User notes
            OutlinedTextField(
                value = uiState.userNotes,
                onValueChange = onUserNotesChange,
                label = { Text("备注") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 2
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Max review rounds
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "最大评审轮数:",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.weight(1f)
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(
                        onClick = { if (uiState.maxReviewRounds > 1) onMaxRoundsChange(uiState.maxReviewRounds - 1) }
                    ) {
                        Icon(Icons.Default.Remove, contentDescription = "减少")
                    }
                    Text(
                        text = "${uiState.maxReviewRounds}",
                        style = MaterialTheme.typography.titleMedium
                    )
                    IconButton(
                        onClick = { if (uiState.maxReviewRounds < 5) onMaxRoundsChange(uiState.maxReviewRounds + 1) }
                    ) {
                        Icon(Icons.Default.Add, contentDescription = "增加")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Button(
                    onClick = onGenerateRecipe,
                    enabled = !uiState.isLoading && uiState.ingredients.any { it.name.isNotBlank() },
                    modifier = Modifier.weight(1f)
                ) {
                    if (uiState.isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("直接生成")
                    }
                }
                
                Button(
                    onClick = onExpertMeeting,
                    enabled = !uiState.isLoading && uiState.ingredients.any { it.name.isNotBlank() },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.secondary
                    )
                ) {
                    Text("专家会议")
                }
            }
            
            // Error display
            if (uiState.error != null) {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = uiState.error,
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }
        }
    }
}

@Composable
private fun SectionTitle(title: String, icon: androidx.compose.ui.graphics.vector.ImageVector) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.padding(vertical = 8.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

@Composable
private fun IngredientInputCard(
    ingredient: IngredientInputUi,
    onUpdate: (IngredientInputUi) -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = ingredient.name,
                    onValueChange = { onUpdate(ingredient.copy(name = it)) },
                    label = { Text("名称") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                Spacer(modifier = Modifier.width(8.dp))
                IconButton(onClick = onDelete) {
                    Icon(Icons.Default.Delete, contentDescription = "删除")
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = ingredient.state,
                    onValueChange = { onUpdate(ingredient.copy(state = it)) },
                    label = { Text("状态") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                OutlinedTextField(
                    value = ingredient.amount,
                    onValueChange = { onUpdate(ingredient.copy(amount = it)) },
                    label = { Text("数量") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
                OutlinedTextField(
                    value = ingredient.unit,
                    onValueChange = { onUpdate(ingredient.copy(unit = it)) },
                    label = { Text("单位") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
            }
        }
    }
}

@Composable
private fun ToolInputCard(
    tool: ToolInputUi,
    onUpdate: (ToolInputUi) -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = tool.name,
                onValueChange = { onUpdate(tool.copy(name = it)) },
                label = { Text("工具名称") },
                modifier = Modifier.weight(1f),
                singleLine = true
            )
            Spacer(modifier = Modifier.width(8.dp))
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "删除")
            }
        }
    }
}

@Composable
private fun ConstraintsInputCard(
    constraints: ConstraintsInputUi,
    onUpdate: (ConstraintsInputUi) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = constraints.goal,
                onValueChange = { onUpdate(constraints.copy(goal = it)) },
                label = { Text("目标 (如: 减脂餐、高蛋白)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = constraints.timeLimitMin,
                    onValueChange = { onUpdate(constraints.copy(timeLimitMin = it)) },
                    label = { Text("时间(分钟)") },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
                OutlinedTextField(
                    value = constraints.difficulty,
                    onValueChange = { onUpdate(constraints.copy(difficulty = it)) },
                    label = { Text("难度") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
            }
            
            OutlinedTextField(
                value = constraints.dietaryRestrictions,
                onValueChange = { onUpdate(constraints.copy(dietaryRestrictions = it)) },
                label = { Text("饮食限制 (用逗号分隔)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
        }
    }
}
