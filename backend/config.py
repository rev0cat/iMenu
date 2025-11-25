"""
Configuration module for the Cooking Expert Committee backend.
"""
import os
from typing import Optional

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cooking_committee.db")

# JWT Configuration
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# LLM Configuration
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # "mock", "openai", etc.
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# Server Configuration
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

# Expert Committee Configuration
DEFAULT_MAX_REVIEW_ROUNDS: int = 1
MAX_ALLOWED_REVIEW_ROUNDS: int = 5
