"""
Main FastAPI application with HTTP and WebSocket endpoints.
"""
import json
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

import config
from db.base import create_db_and_tables, get_session, get_session_context
from db.entities import User
from auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    register_user,
    login_user,
    get_current_user,
)
from auth.dependencies import get_user_from_ws_token
from models import (
    CookingRequest,
    FullRecipe,
    DiscussionEvent,
    FollowUpRequest,
    FollowUpResponse,
    SessionSummary,
    SessionDetail,
)
from services import (
    generate_recipe_sync,
    generate_recipe_stream,
    followup_sync,
    followup_stream,
    get_user_history,
    get_session_detail,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="烹饪专家委员会 API",
    description="多Agent专家委员会做菜系统 - 后端API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================== Authentication Endpoints ==================

@app.post("/auth/register", response_model=TokenResponse, tags=["认证"])
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_session)
):
    """
    注册新用户。
    
    注册成功后自动登录，返回访问令牌。
    """
    user, error = register_user(db, request.email, request.password)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Auto-login after registration
    token_response, _ = login_user(db, request.email, request.password)
    return token_response


@app.post("/auth/login", response_model=TokenResponse, tags=["认证"])
async def login(
    request: LoginRequest,
    db: Session = Depends(get_session)
):
    """
    用户登录。
    
    验证成功后返回JWT访问令牌。
    """
    token_response, error = login_user(db, request.email, request.password)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return token_response


# ================== Recipe Generation Endpoints ==================

@app.post("/generate_recipe", response_model=FullRecipe, tags=["菜谱生成"])
async def generate_recipe(
    request: CookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    同步生成菜谱。
    
    调用专家委员会进行多轮评审，返回最终菜谱。
    需要Bearer Token认证。
    """
    recipe = generate_recipe_sync(db, current_user.id, request)
    return recipe


# ================== History Endpoints ==================

@app.get("/history", response_model=List[SessionSummary], tags=["历史记录"])
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    获取用户的菜谱生成历史列表。
    
    返回每个会话的摘要信息。
    """
    sessions = get_user_history(db, current_user.id, limit, offset)
    return sessions


@app.get("/history/{session_id}", response_model=SessionDetail, tags=["历史记录"])
async def get_history_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    获取指定会话的详细信息。
    
    包含完整的请求、结果和追问记录。
    """
    detail = get_session_detail(db, current_user.id, session_id)
    
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    return detail


# ================== Follow-up Endpoints ==================

@app.post("/history/{session_id}/follow_up", response_model=FollowUpResponse, tags=["追问"])
async def follow_up(
    session_id: int,
    question: str = Query(..., description="追问问题"),
    max_review_rounds: int = Query(1, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    对指定会话发起追问。
    
    专家委员会会基于原有菜谱讨论并回答问题。
    """
    response = followup_sync(
        db,
        current_user.id,
        session_id,
        question,
        max_review_rounds
    )
    return response


# ================== WebSocket Endpoints ==================

@app.websocket("/ws/generate_recipe_stream")
async def websocket_generate_recipe(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket端点：流式生成菜谱。
    
    1. 连接时通过query参数传递token进行认证
    2. 发送CookingRequest JSON消息
    3. 接收流式DiscussionEvent JSON消息
    4. 最后收到event_type="final_summary"表示完成
    """
    await websocket.accept()
    
    try:
        # Authenticate
        with next(get_session_context()) as db:
            user = get_user_from_ws_token(token, db)
            
            if user is None:
                await websocket.send_json({"error": "无效的认证令牌"})
                await websocket.close(code=1008)
                return
            
            user_id = user.id
        
        # Wait for cooking request
        request_data = await websocket.receive_json()
        request = CookingRequest.model_validate(request_data)
        
        # Define event callback
        async def send_event(event: DiscussionEvent):
            event_dict = event.model_dump()
            # Convert datetime to string for JSON serialization
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            await websocket.send_json(event_dict)
        
        # Create sync callback wrapper (LangGraph is sync)
        import asyncio
        
        def sync_callback(event: DiscussionEvent):
            asyncio.get_event_loop().run_until_complete(send_event(event))
        
        # Generate recipe with streaming
        with next(get_session_context()) as db:
            recipe = generate_recipe_stream(db, user_id, request, sync_callback)
        
        # Send final recipe
        await websocket.send_json({
            "event_type": "complete",
            "payload": {
                "recipe": recipe.model_dump()
            }
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        try:
            await websocket.close()
        except:
            pass


@app.websocket("/ws/follow_up_stream")
async def websocket_follow_up(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket端点：流式追问。
    
    1. 连接时通过query参数传递token进行认证
    2. 发送JSON消息：{"session_id": int, "question": str, "max_review_rounds": int}
    3. 接收流式DiscussionEvent JSON消息
    4. 最后收到event_type="followup_answer"表示完成
    """
    await websocket.accept()
    
    try:
        # Authenticate
        with next(get_session_context()) as db:
            user = get_user_from_ws_token(token, db)
            
            if user is None:
                await websocket.send_json({"error": "无效的认证令牌"})
                await websocket.close(code=1008)
                return
            
            user_id = user.id
        
        # Wait for follow-up request
        request_data = await websocket.receive_json()
        session_id = request_data.get("session_id")
        question = request_data.get("question")
        max_review_rounds = request_data.get("max_review_rounds", 1)
        
        if not session_id or not question:
            await websocket.send_json({"error": "缺少session_id或question参数"})
            await websocket.close()
            return
        
        # Define event callback
        async def send_event(event: DiscussionEvent):
            event_dict = event.model_dump()
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            await websocket.send_json(event_dict)
        
        import asyncio
        
        def sync_callback(event: DiscussionEvent):
            asyncio.get_event_loop().run_until_complete(send_event(event))
        
        # Process follow-up with streaming
        with next(get_session_context()) as db:
            response = followup_stream(
                db,
                user_id,
                session_id,
                question,
                sync_callback,
                max_review_rounds
            )
        
        # Send final response
        await websocket.send_json({
            "event_type": "complete",
            "payload": {
                "response": response.model_dump()
            }
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        try:
            await websocket.close()
        except:
            pass


# ================== Health Check ==================

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点。"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
