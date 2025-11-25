"""
Authentication dependencies for FastAPI.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from db.base import get_session
from db.entities import User
from auth.service import verify_token, get_user_from_token


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user from HTTP Authorization header.
    """
    token = credentials.credentials
    user = get_user_from_token(session, token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_ws(
    token: str = Query(...),
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user from WebSocket query parameter.
    """
    user = get_user_from_token(session, token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    return user


def get_user_from_ws_token(token: str, session: Session) -> Optional[User]:
    """
    Helper function to get user from WebSocket token.
    Returns None if invalid.
    """
    return get_user_from_token(session, token)
