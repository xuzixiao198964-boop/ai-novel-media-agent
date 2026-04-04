# -*- coding: utf-8 -*-
"""发布API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import User, Publish, PlatformAccount, PublishStatus
from app.core.deps import get_current_user

router = APIRouter()


@router.post("/platforms")
async def bind_platform(
    platform_type: str,
    access_token: str,
    account_name: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """绑定平台账号"""
    if platform_type not in ["douyin", "xiaohongshu", "fanqiao", "qidian"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的平台类型"
        )

    # 检查是否已绑定
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == current_user.id,
            PlatformAccount.platform_type == platform_type
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 更新
        existing.access_token = access_token
        existing.account_name = account_name
        existing.is_active = True
    else:
        # 创建
        platform = PlatformAccount(
            user_id=current_user.id,
            platform_type=platform_type,
            access_token=access_token,
            account_name=account_name,
            is_active=True
        )
        db.add(platform)

    await db.commit()

    return {"message": "平台账号绑定成功"}


@router.get("/platforms")
async def list_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取已绑定的平台账号"""
    result = await db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == current_user.id)
    )
    platforms = result.scalars().all()

    return {"items": platforms}


@router.delete("/platforms/{platform_id}")
async def unbind_platform(
    platform_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """解绑平台账号"""
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.id == platform_id,
            PlatformAccount.user_id == current_user.id
        )
    )
    platform = result.scalar_one_or_none()

    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="平台账号不存在"
        )

    await db.delete(platform)
    await db.commit()

    return {"message": "平台账号已解绑"}


@router.post("/content/{content_type}/{content_id}")
async def publish_content(
    content_type: str,  # novel, video
    content_id: int,
    platform_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发布内容到平台"""
    if content_type not in ["novel", "video"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的内容类型"
        )

    # 验证平台账号
    for platform_id in platform_ids:
        result = await db.execute(
            select(PlatformAccount).where(
                PlatformAccount.id == platform_id,
                PlatformAccount.user_id == current_user.id,
                PlatformAccount.is_active == True
            )
        )
        platform = result.scalar_one_or_none()

        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"平台账号 {platform_id} 不存在或未激活"
            )

        # 创建发布记录
        publish = Publish(
            content_id=content_id,
            content_type=content_type,
            platform_id=platform_id,
            status=PublishStatus.PENDING
        )
        db.add(publish)

    await db.commit()

    # TODO: 提交到发布队列

    return {"message": "发布任务已创建"}


@router.get("/history")
async def publish_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取发布历史"""
    # 获取用户的所有平台账号ID
    platform_result = await db.execute(
        select(PlatformAccount.id).where(PlatformAccount.user_id == current_user.id)
    )
    platform_ids = [row[0] for row in platform_result.all()]

    if not platform_ids:
        return {"total": 0, "items": []}

    # 查询发布记录
    result = await db.execute(
        select(Publish)
        .where(Publish.platform_id.in_(platform_ids))
        .order_by(desc(Publish.created_at))
        .offset(skip)
        .limit(limit)
    )
    publishes = result.scalars().all()

    return {"total": len(publishes), "items": publishes}
