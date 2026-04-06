from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/app.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    secret_key: str = "dev-secret-key-change-in-production"  # 小写别名
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    access_token_expire_minutes: int = 30  # 小写别名
    refresh_token_expire_days: int = 7
    api_key_salt: str = "api-key-salt-change-in-production"

    # 密码策略
    password_min_length: int = 6
    password_require_uppercase: bool = False
    password_require_lowercase: bool = False
    password_require_digit: bool = False
    password_require_special: bool = False

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
        case_sensitive = False  # 不区分大小写
        extra = "allow"  # 允许额外字段

settings = Settings()
