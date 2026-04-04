# -*- coding: utf-8 -*-
"""用户API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, UserPackage, Package
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
    result = await db.execute(
        select(Package).where(Package.is_active == True).order_by(Package.sort_order)
    )
    packages = result.scalars().all()

    return {"items": packages}


@router.get("/packages/current")
async def get_current_package(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前套餐"""
    result = await db.execute(
        select(UserPackage).where(
            UserPackage.user_id == current_user.id,
            UserPackage.status == "active"
        ).order_by(UserPackage.started_at.desc())
    )
    user_package = result.scalar_one_or_none()

    if not user_package:
        return {"message": "未订阅套餐"}

    # 获取套餐详情
    package_result = await db.execute(
        select(Package).where(Package.id == user_package.package_id)
    )
    package = package_result.scalar_one_or_none()

    return {
        "user_package": user_package,
        "package": package
    }


@router.post("/packages/{package_id}/subscribe")
async def subscribe_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """订阅套餐"""
    # 验证套餐存在
    result = await db.execute(
        select(Package).where(Package.id == package_id, Package.is_active == True)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="套餐不存在"
        )

    # TODO: 实现套餐订阅逻辑（支付、创建订阅记录等）

    return {"message": "套餐订阅成功"}
