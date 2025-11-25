# iMenu - Cooking Committee Skeleton

This repository provides a runnable scaffold for the multi-agent cooking committee system with a FastAPI backend and an Android (Jetpack Compose) client.

## Backend (Python + FastAPI + LangGraph)
- Entry: `backend/app.py` (HTTP + WebSocket)
- Requirements: `pip install -r requirements.txt`
- Run: `uvicorn backend.app:app --reload`
- Key modules: models, LangGraph nodes/graphs, mock LLM, JWT auth, SQLite persistence via SQLModel.

### Example HTTP usage
```bash
# register
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"pass"}'
# login
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d 'username=user@example.com&password=pass'
# generate recipe
curl -X POST http://localhost:8000/generate_recipe -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"ingredients":[{"name":"chicken","state":"raw"}],"tools":[{"name":"pan"}],"constraints":{"goal":"high protein"},"user_notes":"spicy"}'
# history
curl -H "Authorization: Bearer <token>" http://localhost:8000/history
```

### Example WebSocket usage
- Connect: `ws://localhost:8000/ws/generate_recipe_stream?token=<jwt>`
- First message: send `CookingRequest` JSON payload.
- Server streams `DiscussionEvent` JSON objects, ending with `event_type="final_summary"`.

## Android client (Kotlin + Compose + Material3)
- Project path: `android-client/`
- Configure endpoints: HTTP `http://10.0.2.2:8000`, WS `ws://10.0.2.2:8000`
- Core screens: Auth, Input, Discussion timeline, Result. Uses Retrofit + OkHttp WebSocket + kotlinx.serialization.
- Build with Android Gradle Plugin 8 and Kotlin 1.9.

This skeleton focuses on a clear separation of concerns and can be expanded with real LLM providers, richer LangGraph flows, DataStore-backed token storage, and full UI state management.
