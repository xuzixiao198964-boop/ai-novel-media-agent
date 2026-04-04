from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/app.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None

    # LLM配置
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 9000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外字段

settings = Settings()
