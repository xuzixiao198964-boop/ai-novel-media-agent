# -*- coding: utf-8 -*-
"""用户API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户资料"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "nickname": current_user.nickname,
        "avatar_url": current_user.avatar_url,
        "balance": current_user.balance,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }


@router.patch("/profile")
async def update_profile(
    nickname: str = None,
    avatar_url: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户资料"""
    if nickname:
        current_user.nickname = nickname
    if avatar_url:
        current_user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(current_user)

    return {"message": "资料更新成功"}


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user)
):
    """获取账户余额"""
    return {"balance": current_user.balance}


@router.get("/packages")
async def list_packages(
    db: AsyncSession = Depends(get_db)
):
    """获取所有套餐"""
    # 返回固定的套餐列表
    packages = [
        {
            "id": 1,
            "name": "基础版",
            "price": 99.0,
            "duration_days": 30,
            "features": ["每日10次小说生成", "每日5次视频生成", "基础模板"],
            "is_active": True
        },
        {
            "id": 2,
            "name": "专业版",
            "price": 299.0,
            "duration_days": 30,
            "features": ["每日50次小说生成", "每日20次视频生成", "高级模板", "优先处理"],
            "is_active": True
        },
        {
            "id": 3,
            "name": "企业版",
            "price": 999.0,
            "duration_days": 30,
            "features": ["无限小说生成", "无限视频生成", "全部模板", "专属客服"],
            "is_active": True
        }
    ]
    return {"items": packages}


@router.get("/packages/current")
async def get_current_package(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前套餐"""
    # 返回用户的订阅等级
    return {
        "subscription_tier": current_user.subscription_tier,
        "message": "当前套餐信息"
    }


@router.post("/packages/{package_id}/subscribe")
async def subscribe_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """订阅套餐"""
    # TODO: 实现套餐订阅逻辑（支付、创建订阅记录等）
    return {"message": "套餐订阅成功"}
