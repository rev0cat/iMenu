# iMenu 专家委员会菜谱系统

本仓库包含**FastAPI 后端**与**Android Jetpack Compose 客户端**的可运行骨架，覆盖注册/登录、专家委员会多轮评审生成菜谱、追问追踪、WebSocket 流式事件等全流程。默认提供基于 SQLite 的轻量持久化与 Mock LLM，开箱即用。

## 后端概览
- 技术栈：Python 3.10+、FastAPI、SQLModel + SQLite、JWT、LangGraph、Uvicorn、pydantic。
- 主要模块：
  - `backend/app.py`：HTTP + WebSocket 入口，统一鉴权。
  - `backend/agents/*`：专家角色、节点实现。
  - `backend/graphs/*`：LangGraph 构建的多轮流程（生成 / 追问）。
  - `backend/services/*`：业务封装（同步 + 流式）。
  - `backend/db/*`：SQLModel 实体、CRUD 仓储。
  - `backend/llm/mock_client.py`：可离线运行的 Mock LLM。

### 本地运行
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

### HTTP API 示例
1. 注册 `POST /auth/register`：`{"email":"foo@bar.com","password":"secret"}`
2. 登录 `POST /auth/login`：获取 `access_token`
3. 生成菜谱 `POST /generate_recipe`（需 Bearer Token）：
```json
{
  "ingredients": [{"name":"鸡胸肉","state":"raw","amount":200,"unit":"g"}],
  "tools": [{"name":"炒锅"}],
  "constraints": {"goal":"高蛋白","time_limit_min":20},
  "user_notes": "少油低盐",
  "max_review_rounds": 2
}
```
4. 历史列表 `GET /history`，详情 `GET /history/{id}`
5. 追问 `POST /history/{id}/follow_up`：`{"session_id":1,"question":"能否更辣？","max_review_rounds":1}`

### WebSocket 流式示例
- 连接：`ws://localhost:8000/ws/generate_recipe_stream?token=<JWT>`
- 首条消息：发送 `CookingRequest` JSON（同上）。
- 服务端按时间线推送 `DiscussionEvent`：`planning_started` → `initial_plan` → `expert_opinion` → `expert_objection` → `objection_response` → `chair_decision` → `final_summary`。
- 追问流式：`ws://localhost:8000/ws/follow_up_stream?token=<JWT>`，发送 `{ "session_id": 1, "question": "...", "max_review_rounds": 1 }`，事件包含 `followup_question`、`expert_opinion`、`followup_answer`。

### 数据持久化
- SQLite 默认文件：`sqlite:///./cooking.db`
- 实体：User、RecipeSession、DiscussionEventRecord、FollowUpRecord
- `repositories.py` 内置 CRUD（创建会话、保存事件、追问记录等）。

### 运行要点
- LangGraph 图在 `backend/graphs/recipe_graph.py`、`followup_graph.py` 内构建，可同步 `run` 也可异步 `astream`。
- WebSocket 端口复用 JWT，事件在生成线程中通过 `asyncio.run_coroutine_threadsafe` 推送。
- Mock LLM 返回可读示例，替换为真实 LLM 只需实现 `llm/base.py` 接口。

## Android 客户端概览
- 技术栈：Kotlin、Jetpack Compose、Material 3、Retrofit + OkHttp + Kotlinx Serialization。
- 项目结构：
  - `android-client/app/src/main/java/com/example/cookingcommittee/MainActivity.kt`：入口 + NavHost。
  - `navigation/NavGraph.kt`：Auth / Input / Discussion / Result / History 路由。
  - `data/api`、`data/model`、`data/ws`：HTTP 与 WebSocket DTO、客户端封装。
  - `ui/screen/*`：Compose 界面（可直接连接 ViewModel/Repository）。
- 网络配置：模拟器访问本机请设置
  - `BASE_URL = "http://10.0.2.2:8000/"`
  - `BASE_URL_WS = "ws://10.0.2.2:8000/"`
- WebSocket 消费 `DiscussionEventDto`，在 `DiscussionScreen` 的 `LazyColumn` 以时间线展示，多轮事件会实时追加。

## 快速检查
- 后端启动：`uvicorn backend.app:app --reload --port 8000`
- 注册/登录/生成：使用上方 curl 示例
- WebSocket：可使用 `wscat` 或浏览器调试查看事件流

## 下一步扩展建议
- 将 Mock LLM 替换为真实模型（OpenAI/讯飞等），并在节点内切换流式生成
- 增加前端 DataStore Token 持久化、Repository + ViewModel
- 完善历史重放页面：从 `DiscussionEventRecord` 还原时间线
- 为后端添加 pytest/async WebSocket 集成测试
