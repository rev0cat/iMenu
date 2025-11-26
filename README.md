# iMenu 专家委员会菜谱系统

本仓库包含**FastAPI 后端**与**Android Jetpack Compose 客户端**的可运行骨架，覆盖注册/登录、专家委员会多轮评审生成菜谱、追问追踪、WebSocket 流式事件等全流程。后端默认直连真实 LLM，可通过配置切换 qwen / deepseek / gemini / OpenAI 兼容接口。

## 后端概览
- 技术栈：Python 3.10+、FastAPI、SQLModel + SQLite、JWT、LangGraph、Uvicorn、pydantic。
- 主要模块：
  - `backend/app.py`：HTTP + WebSocket 入口，统一鉴权。
  - `backend/agents/*`：专家角色、节点实现。
  - `backend/graphs/*`：LangGraph 构建的多轮流程（生成 / 追问）。
  - `backend/services/*`：业务封装（同步 + 流式）。
  - `backend/db/*`：SQLModel 实体、CRUD 仓储。
  - `backend/llm/factory.py`：根据配置选择 LLM（qwen / deepseek / gemini / OpenAI 兼容）。

### 本地运行
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

### LLM 配置示例
支持 OpenAI 兼容接口（含 qwen 兼容模式、deepseek 等）和 Gemini，使用 `.env` 或环境变量即可。

- Qwen 兼容模式（DashScope）：
```env
llm_provider=qwen
llm_api_key=YOUR_DASHSCOPE_KEY
llm_model=qwen-plus
# 如需自定义兼容模式地址：llm_base_url=https://dashscope.aliyuncs.com/compatible-mode
```

- DeepSeek：
```env
llm_provider=deepseek
llm_api_key=YOUR_DEEPSEEK_KEY
llm_model=deepseek-chat
```

- Gemini：
```env
llm_provider=gemini
gemini_api_key=YOUR_GEMINI_KEY
gemini_model=gemini-1.5-flash
```

未提供 key 时会直接抛出异常，确保启动前已配置。

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
- LLM 通过 `backend/llm/factory.py` 选择，支持流式返回；未配置 key 会在启动时抛出异常，便于提前发现问题。

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
- 将 LLM 接入生产可用的 OpenAI 兼容 / Gemini 端点，并在节点内切换流式生成
- 增加前端 DataStore Token 持久化、Repository + ViewModel
- 完善历史重放页面：从 `DiscussionEventRecord` 还原时间线
- 为后端添加 pytest/async WebSocket 集成测试
