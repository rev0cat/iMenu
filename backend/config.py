from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Cooking Committee"
    database_url: str = "sqlite:///./app.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    llm_provider: str = "mock"


settings = Settings()
