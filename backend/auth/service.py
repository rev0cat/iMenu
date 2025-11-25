from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from backend.config import get_settings
from backend.db import repositories
from backend.db.entities import User
from .schemas import RegisterRequest, LoginRequest, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def register_user(data: RegisterRequest) -> TokenResponse:
    existing = repositories.get_user_by_email(data.email)
    if existing:
        raise ValueError("User already exists")
    user = repositories.create_user(email=data.email, password_hash=hash_password(data.password))
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


def authenticate_user(data: LoginRequest) -> TokenResponse:
    user = repositories.get_user_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid credentials")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


def get_user_from_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload.get("sub"))
    except Exception:
        return None
    return repositories.get_user(user_id)

