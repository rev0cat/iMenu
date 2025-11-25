from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Cooking Committee"
    database_url: str = "sqlite:///./cooking.db"
    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    llm_provider: str = "mock"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

