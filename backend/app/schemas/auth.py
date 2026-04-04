# -*- coding: utf-8 -*-
"""Pydantic数据模型 - 认证相关"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    balance: float
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class PasswordReset(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)
