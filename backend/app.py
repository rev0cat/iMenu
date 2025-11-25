import json
from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from backend import models
from backend.auth import dependencies as auth_dependencies
from backend.auth import schemas as auth_schemas
from backend.auth import service as auth_service
from backend.db.base import init_db
from backend.db.session import get_session
from backend.services import recipe_service, followup_service, history_service

app = FastAPI(title="Cooking Committee")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/auth/register", response_model=auth_schemas.TokenResponse)
def register_user(request: auth_schemas.RegisterRequest, session=Depends(get_session)):
    user = auth_service.register_user(session, request)
    return auth_service.generate_token_for_user(user)


@app.post("/auth/login", response_model=auth_schemas.TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    request = auth_schemas.LoginRequest(email=form_data.username, password=form_data.password)
    user = auth_service.authenticate_user(session, request)
    return auth_service.generate_token_for_user(user)


@app.post("/generate_recipe", response_model=models.FullRecipe)
def generate_recipe(
    request: models.CookingRequest, current_user=Depends(auth_dependencies.get_current_user)
):
    return recipe_service.generate_recipe_sync(current_user.id, request)


@app.get("/history")
def list_history(limit: int = 20, offset: int = 0, current_user=Depends(auth_dependencies.get_current_user)):
    sessions = history_service.list_user_sessions(current_user.id, limit, offset)
    return [
        {
            "id": s.id,
            "created_at": s.created_at,
            "rounds_used": s.rounds_used,
            "dish_name": s.result_json.get("dish", {}).get("name"),
            "goal": s.request_json.get("constraints", {}).get("goal"),
        }
        for s in sessions
    ]


@app.get("/history/{session_id}")
def get_history_detail(session_id: int, current_user=Depends(auth_dependencies.get_current_user)):
    result = history_service.get_session_detail(current_user.id, session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    record, followups = result
    return {
        "session": record,
        "followups": followups,
    }


@app.post("/history/{session_id}/follow_up", response_model=models.FollowUpResponse)
def follow_up(
    session_id: int,
    request: models.FollowUpRequest,
    current_user=Depends(auth_dependencies.get_current_user),
):
    max_rounds = request.max_review_rounds or 1
    return followup_service.followup_sync(current_user.id, session_id, request.question, max_rounds)


@app.websocket("/ws/generate_recipe_stream")
async def websocket_recipe(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return
    user_payload = auth_service.decode_token(token)
    user_id = int(user_payload.get("sub"))
    await websocket.accept()
    try:
        raw_request = await websocket.receive_text()
        request_data = json.loads(raw_request)
        request = models.CookingRequest(**request_data)
    except Exception:
        await websocket.close(code=4002)
        return

    async def send_event(event: models.DiscussionEvent) -> None:
        await websocket.send_text(event.json())

    recipe = recipe_service.generate_recipe_stream(user_id, request, send_event)
    await websocket.send_text(
        models.DiscussionEvent(event_type="final_summary", payload=recipe.dict()).json()
    )
    await websocket.close()


@app.websocket("/ws/follow_up_stream")
async def websocket_followup(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return
    user_payload = auth_service.decode_token(token)
    user_id = int(user_payload.get("sub"))
    await websocket.accept()
    try:
        raw_request = await websocket.receive_text()
        request_data = json.loads(raw_request)
        session_id = int(request_data["session_id"])
        question = request_data.get("question", "")
        max_rounds = request_data.get("max_review_rounds", 1)
    except Exception:
        await websocket.close(code=4002)
        return

    async def send_event(event: models.DiscussionEvent) -> None:
        await websocket.send_text(event.json())

    followup_service.followup_stream(user_id, session_id, question, max_rounds, send_event)
    await websocket.send_text(
        models.DiscussionEvent(event_type="followup_answer", payload={"text": "Follow-up done"}).json()
    )
    await websocket.close()
