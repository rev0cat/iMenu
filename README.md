# iMenu Cooking Committee

This repository provides a dual-stack skeleton: a FastAPI backend orchestrating a multi-agent recipe committee and an Android (Kotlin + Jetpack Compose) client that visualizes expert discussions via HTTP and WebSocket streaming.

## Backend

**Tech:** FastAPI, SQLModel + SQLite, JWT auth, LangGraph-style orchestration, Mock LLM client.

### Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

### API quickstart

1. Register: `POST /auth/register` with `{ "email": "foo@bar.com", "password": "secret" }`
2. Login: `POST /auth/login` to obtain `access_token`.
3. Generate recipe: `POST /generate_recipe` with `Authorization: Bearer <token>` and a `CookingRequest` body.
4. List history: `GET /history`
5. Follow-up: `POST /history/{id}/follow_up` with `{ "session_id": 1, "question": "Add more spice?" }`

### WebSocket streaming

- Connect: `ws://localhost:8000/ws/generate_recipe_stream?token=<JWT>`
- Send one JSON payload matching `CookingRequest`.
- Receive `DiscussionEvent` objects such as `planning_started`, `expert_opinion`, `chair_decision`, `final_summary`.

## Android client

**Tech:** Kotlin, Jetpack Compose, Material 3, Retrofit + OkHttp (HTTP + WebSocket), Kotlinx Serialization.

### Project layout

- `MainActivity` + `NavGraph` wire authentication, input, discussion, results, and history screens.
- `data/api` hosts Retrofit interfaces (`AuthApiService`, `RecipeApiService`).
- `data/ws/RecipeWebSocketClient` streams `DiscussionEventDto` updates to UI state.
- Screens (`ui/screen/*.kt`) are lightweight Compose samples ready to be connected to repositories/ViewModels.

### Emulator configuration

Set `BASE_URL` to `http://10.0.2.2:8000/` and WebSocket base to `ws://10.0.2.2:8000/` when running the backend locally via Android emulator.

