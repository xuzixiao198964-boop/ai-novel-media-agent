# -*- coding: utf-8 -*-
"""OpenClaw协议API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Task
from app.core.deps import verify_api_key_header

router = APIRouter()


@router.get("/capabilities")
async def get_capabilities():
    """获取平台能力（OpenClaw标准）"""
    return {
        "protocol": "openclaw/1.0",
        "platform": "AI智能内容创作平台",
        "version": "2.0.0",
        "capabilities": [
            {
                "id": "novel_generation",
                "name": "小说生成",
                "description": "AI自动生成小说（微/短/中/长/超长篇）",
                "types": ["micro", "short", "medium", "long", "super_long"],
                "genres": ["children", "male", "female"]
            },
            {
                "id": "video_generation",
                "name": "视频生成",
                "description": "从小说或资讯自动生成视频",
                "sources": ["ai_novel", "external_novel", "news"]
            },
            {
                "id": "multi_platform_publish",
                "name": "多平台发布",
                "description": "自动发布到抖音、小红书、番茄小说等平台",
                "platforms": ["douyin", "xiaohongshu", "fanqiao", "qidian"]
            }
        ]
    }


@router.get("/tasks")
async def list_tasks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(verify_api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表（OpenClaw标准）"""
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    return {
        "protocol": "openclaw/1.0",
        "tasks": [
            {
                "id": task.task_id,
                "type": task.type.value,
                "status": task.status.value,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]
    }


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    current_user: User = Depends(verify_api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情（OpenClaw标准）"""
    result = await db.execute(
        select(Task).where(
            Task.task_id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    return {
        "protocol": "openclaw/1.0",
        "task": {
            "id": task.task_id,
            "type": task.type.value,
            "status": task.status.value,
            "progress": task.progress,
            "current_step": task.current_step,
            "config": task.config_json,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error_message
        }
    }


@router.get("/tasks/{task_id}/output")
async def get_task_output(
    task_id: str,
    current_user: User = Depends(verify_api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """获取任务产出（OpenClaw标准）"""
    result = await db.execute(
        select(Task).where(
            Task.task_id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    if task.status.value != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务尚未完成"
        )

    # TODO: 返回实际产出（小说/视频链接等）

    return {
        "protocol": "openclaw/1.0",
        "task_id": task.task_id,
        "outputs": []
    }


@router.post("/tasks")
async def create_task(
    task_data: dict,
    current_user: User = Depends(verify_api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """创建任务（OpenClaw标准）"""
    # TODO: 实现任务创建逻辑
    return {
        "protocol": "openclaw/1.0",
        "message": "任务创建成功",
        "task_id": "task_xxx"
    }
