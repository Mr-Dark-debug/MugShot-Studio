from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tmughsot studio"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str

    # Providers
    GEMINI_API_KEY: str
    BYTEDANCE_API_KEY: str
    FAL_KEY: str

    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Sentry
    SENTRY_DSN: Union[str, None] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()