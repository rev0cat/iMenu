"""
Authentication service for user registration, login, and JWT handling.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

import config
from db.repositories import get_user_by_email, create_user as db_create_user, get_user_by_id
from db.entities import User
from auth.schemas import TokenResponse


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[int]:
    """
    Verify a JWT token and return the user_id if valid.
    Returns None if invalid.
    """
    try:
        payload = jwt.decode(
            token, 
            config.JWT_SECRET_KEY, 
            algorithms=[config.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)
    except JWTError:
        return None


def register_user(session: Session, email: str, password: str) -> tuple[Optional[User], Optional[str]]:
    """
    Register a new user.
    Returns (user, error_message).
    """
    # Check if email already exists
    existing = get_user_by_email(session, email)
    if existing:
        return None, "Email already registered"
    
    # Hash password and create user
    password_hash = hash_password(password)
    user = db_create_user(session, email, password_hash)
    
    return user, None


def login_user(session: Session, email: str, password: str) -> tuple[Optional[TokenResponse], Optional[str]]:
    """
    Login a user and return a token.
    Returns (token_response, error_message).
    """
    user = get_user_by_email(session, email)
    if not user:
        return None, "Invalid email or password"
    
    if not verify_password(password, user.password_hash):
        return None, "Invalid email or password"
    
    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token), None


def get_user_from_token(session: Session, token: str) -> Optional[User]:
    """Get user from JWT token."""
    user_id = verify_token(token)
    if user_id is None:
        return None
    return get_user_by_id(session, user_id)
