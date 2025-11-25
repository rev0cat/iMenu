import json
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import get_settings
from backend.db.base import init_db
from backend.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from backend.auth.service import register_user, authenticate_user, get_user_from_token
from backend.auth.dependencies import get_current_user
from backend.models import CookingRequest, FollowUpRequest
from backend.services import recipe_service, followup_service
from backend.db import repositories
from backend.models import DiscussionEvent

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/auth/register", response_model=TokenResponse)
def register(data: RegisterRequest):
    try:
        return register_user(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest):
    try:
        return authenticate_user(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/generate_recipe")
def generate_recipe(request: CookingRequest, user=Depends(get_current_user)):
    recipe = recipe_service.generate_recipe_sync(user.id, request)
    return recipe


@app.get("/history")
def history(limit: int = 20, offset: int = 0, user=Depends(get_current_user)):
    sessions = repositories.list_sessions_by_user(user.id, limit=limit, offset=offset)
    return sessions


@app.get("/history/{session_id}")
def history_detail(session_id: int, user=Depends(get_current_user)):
    session = repositories.get_session_by_id(user.id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Not found")
    followups = repositories.list_followups(session_id)
    return {"session": session, "followups": followups}


@app.post("/history/{session_id}/follow_up")
def follow_up(session_id: int, request: FollowUpRequest, user=Depends(get_current_user)):
    response = followup_service.followup_sync(user.id, session_id, request.question, request.max_review_rounds or 1)
    return response


@app.websocket("/ws/generate_recipe_stream")
async def ws_generate_recipe(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = get_user_from_token(token) if token else None
    if not user:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request = CookingRequest(**json.loads(data))

        import asyncio

        def callback(event: DiscussionEvent):
            asyncio.create_task(websocket.send_text(json.dumps(event.dict())))

        recipe_service.generate_recipe_stream(user.id, request, event_callback=callback)
        await websocket.send_text(json.dumps({"event_type": "stream_completed"}))
    except WebSocketDisconnect:
        return


@app.websocket("/ws/follow_up_stream")
async def ws_follow_up(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = get_user_from_token(token) if token else None
    if not user:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        request = FollowUpRequest(**payload)

        import asyncio

        def callback(event: DiscussionEvent):
            asyncio.create_task(websocket.send_text(json.dumps(event.dict())))

        followup_service.followup_stream(
            user.id,
            request.session_id,
            request.question,
            request.max_review_rounds or 1,
            event_callback=callback,
        )
        await websocket.send_text(json.dumps({"event_type": "stream_completed"}))
    except WebSocketDisconnect:
        return


@app.get("/")
def root():
    return {"message": "Cooking committee backend running"}

