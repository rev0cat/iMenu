from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session
from fastapi import HTTPException, status
from backend.config import settings
from backend.db import repositories
from backend.auth import schemas
from backend.db.entities import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def register_user(session: Session, request: schemas.RegisterRequest) -> User:
    existing = repositories.get_user_by_email(session, request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    password_hash = hash_password(request.password)
    return repositories.create_user(session, request.email, password_hash)


def authenticate_user(session: Session, request: schemas.LoginRequest) -> User:
    user = repositories.get_user_by_email(session, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def generate_token_for_user(user: User) -> schemas.TokenResponse:
    token = create_access_token({"sub": str(user.id)}, timedelta(minutes=settings.jwt_expire_minutes))
    return schemas.TokenResponse(access_token=token)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # propagate HTTPException outside
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return payload
