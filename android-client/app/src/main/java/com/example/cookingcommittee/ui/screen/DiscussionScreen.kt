package com.example.cookingcommittee.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.cookingcommittee.data.model.DiscussionItemUi
import com.example.cookingcommittee.data.model.DiscussionType
import com.example.cookingcommittee.ui.state.DiscussionUiState

/**
 * Discussion screen showing expert committee deliberations.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiscussionScreen(
    uiState: DiscussionUiState,
    onNavigateBack: () -> Unit,
    onViewResult: () -> Unit,
    modifier: Modifier = Modifier
) {
    val listState = rememberLazyListState()
    
    // Auto-scroll to bottom when new events arrive
    LaunchedEffect(uiState.events.size) {
        if (uiState.events.isNotEmpty()) {
            listState.animateScrollToItem(uiState.events.size - 1)
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("专家会议") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ),
                actions = {
                    if (uiState.isComplete && uiState.finalRecipe != null) {
                        TextButton(onClick = onViewResult) {
                            Text("查看结果")
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Status bar
            StatusBar(
                isConnected = uiState.isConnected,
                currentRound = uiState.currentRound,
                isComplete = uiState.isComplete
            )
            
            // Events list
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                contentPadding = PaddingValues(vertical = 16.dp)
            ) {
                items(uiState.events) { event ->
                    DiscussionEventItem(event = event)
                }
                
                // Loading indicator
                if (uiState.isLoading && !uiState.isComplete) {
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Center
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("专家讨论中...", style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            }
            
            // Error display
            if (uiState.error != null) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
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
private fun StatusBar(
    isConnected: Boolean,
    currentRound: Int,
    isComplete: Boolean
) {
    Surface(
        color = when {
            isComplete -> MaterialTheme.colorScheme.tertiaryContainer
            isConnected -> MaterialTheme.colorScheme.secondaryContainer
            else -> MaterialTheme.colorScheme.surfaceVariant
        },
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = when {
                        isComplete -> Icons.Default.CheckCircle
                        isConnected -> Icons.Default.Wifi
                        else -> Icons.Default.WifiOff
                    },
                    contentDescription = null,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = when {
                        isComplete -> "会议结束"
                        isConnected -> "连接中"
                        else -> "等待连接"
                    },
                    style = MaterialTheme.typography.bodySmall
                )
            }
            
            if (currentRound > 0) {
                Text(
                    text = "第 $currentRound 轮",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
private fun DiscussionEventItem(event: DiscussionItemUi) {
    val (backgroundColor, iconTint) = when (event.type) {
        DiscussionType.PLANNING_STARTED, DiscussionType.INITIAL_PLAN -> 
            MaterialTheme.colorScheme.primaryContainer to MaterialTheme.colorScheme.primary
        DiscussionType.EXPERT_OPINION -> 
            MaterialTheme.colorScheme.secondaryContainer to MaterialTheme.colorScheme.secondary
        DiscussionType.EXPERT_OBJECTION -> 
            MaterialTheme.colorScheme.errorContainer to MaterialTheme.colorScheme.error
        DiscussionType.OBJECTION_RESPONSE -> 
            MaterialTheme.colorScheme.tertiaryContainer to MaterialTheme.colorScheme.tertiary
        DiscussionType.CHAIR_DECISION -> 
            MaterialTheme.colorScheme.primaryContainer to MaterialTheme.colorScheme.primary
        DiscussionType.FINAL_SUMMARY, DiscussionType.COMPLETE -> 
            MaterialTheme.colorScheme.tertiaryContainer to MaterialTheme.colorScheme.tertiary
        DiscussionType.ERROR -> 
            MaterialTheme.colorScheme.errorContainer to MaterialTheme.colorScheme.error
        else -> 
            MaterialTheme.colorScheme.surfaceVariant to MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    val icon = when (event.type) {
        DiscussionType.PLANNING_STARTED -> Icons.Default.PlayArrow
        DiscussionType.INITIAL_PLAN -> Icons.Default.Lightbulb
        DiscussionType.EXPERT_OPINION -> Icons.Default.Person
        DiscussionType.EXPERT_OBJECTION -> Icons.Default.Warning
        DiscussionType.OBJECTION_RESPONSE -> Icons.Default.Reply
        DiscussionType.CHAIR_DECISION -> Icons.Default.Gavel
        DiscussionType.FINAL_SUMMARY, DiscussionType.COMPLETE -> Icons.Default.CheckCircle
        DiscussionType.ERROR -> Icons.Default.Error
        else -> Icons.Default.Info
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                
                if (event.expertName != null) {
                    Text(
                        text = event.expertName,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = iconTint
                    )
                    
                    if (event.targetExpert != null) {
                        Text(
                            text = " → ${event.targetExpert}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                } else {
                    Text(
                        text = when (event.type) {
                            DiscussionType.PLANNING_STARTED -> "开始规划"
                            DiscussionType.INITIAL_PLAN -> "初始方案"
                            DiscussionType.ROUND_STARTED -> "第 ${event.roundIndex} 轮开始"
                            DiscussionType.ROUND_FINISHED -> "第 ${event.roundIndex} 轮结束"
                            DiscussionType.FINAL_SUMMARY -> "最终总结"
                            DiscussionType.COMPLETE -> "会议完成"
                            DiscussionType.ERROR -> "错误"
                            else -> event.type.name
                        },
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = iconTint
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = event.text,
                style = MaterialTheme.typography.bodyMedium
            )
            
            if (event.isPartial) {
                Spacer(modifier = Modifier.height(4.dp))
                LinearProgressIndicator(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(2.dp)
                )
            }
        }
    }
}
