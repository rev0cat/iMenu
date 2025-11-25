# 🍳 iMenu - 智能烹饪专家委员会系统

一个基于多 Agent 的智能做菜推荐系统，通过专家委员会讨论机制生成个性化菜谱。

## 📋 项目概述

本项目实现了一个完整的智能做菜系统，包括：

- **后端**：Python + FastAPI + LangGraph 的多 Agent「专家委员会」做菜系统
- **前端**：Android 原生 APK（Kotlin + Jetpack Compose + Material Design 3）
- **通信**：HTTP(JSON) + WebSocket 流式事件
- **存储**：SQLite + SQLModel 轻量级数据库

### 核心功能

1. **智能菜谱生成**：根据用户输入的食材、工具和约束条件，由专家委员会生成详细菜谱
2. **专家委员会讨论**：
   - 多轮评审机制（可配置最大轮数）
   - 专家意见、异议、回应、主席裁决
   - 流式推送讨论过程
3. **用户系统**：注册/登录，JWT 认证
4. **历史记录**：保存每次菜谱生成会话
5. **追问功能**：基于历史会话发起追问，调整方案

## 🏗️ 项目结构

```
iMenu/
├── backend/                    # 后端 Python 代码
│   ├── app.py                 # FastAPI 主入口
│   ├── config.py              # 配置文件
│   ├── models.py              # Pydantic 数据模型
│   ├── state.py               # LangGraph 状态定义
│   ├── requirements.txt       # Python 依赖
│   ├── db/                    # 数据库层
│   │   ├── base.py           # SQLModel 配置
│   │   ├── entities.py       # 数据库实体
│   │   └── repositories.py   # CRUD 操作
│   ├── auth/                  # 认证模块
│   │   ├── schemas.py        # 认证请求/响应模型
│   │   ├── service.py        # 认证服务
│   │   └── dependencies.py   # FastAPI 依赖
│   ├── llm/                   # LLM 抽象层
│   │   ├── base.py           # LLM 接口定义
│   │   └── mock_client.py    # Mock 实现
│   ├── agents/                # 专家 Agent
│   │   ├── roles.py          # 专家角色定义
│   │   ├── nodes.py          # LangGraph 节点
│   │   └── followup_nodes.py # 追问节点
│   ├── graphs/                # LangGraph 工作流
│   │   ├── recipe_graph.py   # 菜谱生成图
│   │   └── followup_graph.py # 追问图
│   └── services/              # 业务服务
│       ├── recipe_service.py
│       ├── followup_service.py
│       └── history_service.py
│
└── android-client/            # Android 前端代码
    └── app/
        └── src/main/
            ├── java/com/example/cookingcommittee/
            │   ├── MainActivity.kt
            │   ├── auth/              # 认证模块
            │   ├── data/              # 数据层
            │   │   ├── api/          # Retrofit API
            │   │   ├── model/        # DTO 模型
            │   │   └── ws/           # WebSocket 客户端
            │   ├── domain/            # 领域层
            │   ├── navigation/        # 导航
            │   └── ui/                # UI 层
            │       ├── screen/       # Compose 屏幕
            │       ├── state/        # UI 状态
            │       └── theme/        # Material 3 主题
            └── res/
```

## 🚀 快速开始

### 后端启动

#### 环境要求
- Python 3.10+
- pip

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 启动服务
```bash
# 开发模式
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python app.py
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### Android 前端

#### 环境要求
- Android Studio Hedgehog (2023.1.1) 或更高版本
- JDK 17
- Android SDK 34

#### 配置

在 `android-client/app/build.gradle.kts` 中配置后端地址：

```kotlin
// 模拟器使用 10.0.2.2 访问本机
buildConfigField("String", "BASE_URL", "\"http://10.0.2.2:8000/\"")
buildConfigField("String", "BASE_URL_WS", "\"ws://10.0.2.2:8000/\"")

// 真机使用实际 IP
// buildConfigField("String", "BASE_URL", "\"http://192.168.1.100:8000/\"")
// buildConfigField("String", "BASE_URL_WS", "\"ws://192.168.1.100:8000/\"")
```

#### 构建运行
1. 用 Android Studio 打开 `android-client` 目录
2. 同步 Gradle
3. 运行 app 模块

## 📡 API 接口

### 认证

#### 注册
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 登录
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 菜谱生成

#### 同步生成菜谱
```bash
curl -X POST "http://localhost:8000/generate_recipe" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {"name": "鸡胸肉", "state": "raw", "amount": 200, "unit": "g"},
      {"name": "西兰花", "state": "raw", "amount": 150, "unit": "g"},
      {"name": "蒜", "state": "raw", "amount": 3, "unit": "瓣"}
    ],
    "tools": [
      {"name": "炒锅"},
      {"name": "菜刀"}
    ],
    "constraints": {
      "goal": "减脂餐",
      "time_limit_min": 30,
      "difficulty": "beginner"
    },
    "max_review_rounds": 2
  }'
```

### 历史记录

#### 获取历史列表
```bash
curl -X GET "http://localhost:8000/history?limit=20&offset=0" \
  -H "Authorization: Bearer <token>"
```

#### 获取会话详情
```bash
curl -X GET "http://localhost:8000/history/1" \
  -H "Authorization: Bearer <token>"
```

### 追问

#### 发起追问
```bash
curl -X POST "http://localhost:8000/history/1/follow_up?question=可以用鸡腿肉替换吗&max_review_rounds=1" \
  -H "Authorization: Bearer <token>"
```

### WebSocket

#### 流式生成菜谱
```javascript
// 连接
const ws = new WebSocket('ws://localhost:8000/ws/generate_recipe_stream?token=<token>');

// 发送请求
ws.send(JSON.stringify({
  "ingredients": [{"name": "鸡胸肉", "state": "raw"}],
  "tools": [{"name": "炒锅"}],
  "constraints": {"goal": "减脂餐"},
  "max_review_rounds": 1
}));

// 接收事件
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.event_type, data.payload);
};
```

#### 流式追问
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/follow_up_stream?token=<token>');

ws.send(JSON.stringify({
  "session_id": 1,
  "question": "这道菜适合孕妇吃吗？",
  "max_review_rounds": 1
}));
```

## 🤖 专家委员会

系统包含以下专家角色：

| 角色 | 职责 |
|------|------|
| 🧑‍🍳 大厨专家 | 烹饪技法、火候控制、调味搭配 |
| 🥗 营养专家 | 营养均衡、热量控制、健康建议 |
| 🔧 工具专家 | 工具选择、流程优化、效率提升 |
| 👶 新手教练 | 难度评估、步骤清晰度、新手友好 |
| ⚠️ 安全专家 | 食品安全、操作安全、风险提示 |
| 🎯 主席 | 意见整合、冲突协调、最终决策 |

### 讨论流程

```
1. 请求规范化
   ↓
2. 初始方案生成
   ↓
3. 专家评审轮次（可多轮）
   │  ├─ 各专家发表意见
   │  ├─ 专家间提出异议
   │  ├─ 被异议专家回应
   │  └─ 主席裁决
   ↓
4. 最终方案输出
```

## 📱 Android 功能

### 屏幕

1. **认证屏幕** - 登录/注册
2. **输入屏幕** - 添加食材、工具、约束条件
3. **讨论屏幕** - 实时查看专家委员会讨论过程
4. **结果屏幕** - 查看生成的菜谱
5. **历史列表** - 查看历史记录
6. **历史详情** - 查看详情并发起追问

### 特性

- Material Design 3 设计语言
- 支持亮/暗主题
- 流式更新讨论过程
- 本地 Token 持久化

## 🔧 配置

### 环境变量（后端）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./cooking_committee.db` |
| `JWT_SECRET_KEY` | JWT 密钥 | `your-secret-key-change-in-production` |
| `JWT_EXPIRE_MINUTES` | Token 过期时间（分钟） | `1440` |
| `LLM_PROVIDER` | LLM 提供者 | `mock` |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `HOST` | 服务地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |

### LLM 配置

目前提供 Mock 实现用于演示，如需接入真实 LLM：

1. 在 `llm/` 目录下实现新的 `LLMClient`
2. 修改 `config.py` 中的 `LLM_PROVIDER`
3. 在 `mock_client.py` 的 `get_llm_client()` 中添加新提供者

## 📊 数据模型

### DiscussionEvent（讨论事件）

```json
{
  "event_type": "expert_opinion",
  "round_index": 1,
  "expert_name": "大厨专家",
  "target_expert": null,
  "payload": {
    "opinion": {
      "comments": "从烹饪技术角度...",
      "suggested_changes_summary": "建议增加火候说明"
    }
  },
  "partial": false,
  "timestamp": "2024-01-01T12:00:00"
}
```

事件类型：
- `planning_started` - 开始规划
- `initial_plan` - 初始方案
- `round_started` - 轮次开始
- `expert_opinion` - 专家意见
- `expert_objection` - 专家异议
- `objection_response` - 异议回应
- `chair_decision` - 主席裁决
- `round_finished` - 轮次结束
- `final_summary` - 最终总结
- `followup_question` - 追问问题
- `followup_answer` - 追问回答

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系

如有问题，请提交 Issue。