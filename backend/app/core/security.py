# -*- coding: utf-8 -*-
"""安全相关：JWT、密码哈希、API Key"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib

from app.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """生成API Key"""
    return f"sk-{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """哈希API Key用于存储"""
    return hashlib.sha256(
        (api_key + settings.api_key_salt).encode()
    ).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """验证API Key"""
    return hash_api_key(api_key) == hashed_key


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """验证密码强度"""
    if len(password) < settings.password_min_length:
        return False, f"密码长度至少{settings.password_min_length}位"

    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"

    if settings.password_require_lowercase and not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"

    if settings.password_require_digit and not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"

    if settings.password_require_special:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "密码必须包含特殊字符"

    return True, None
