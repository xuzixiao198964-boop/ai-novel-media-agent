# -*- coding: utf-8 -*-
"""后台管理API路由 - 完整版"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Task, Novel, Video, Payment, APIKey, PublishRecord, SystemLog, SystemConfig
from app.core.deps import get_current_admin

router = APIRouter()


# ==================== Pydantic Models ====================
class DashboardStats(BaseModel):
    total_users: int
    today_new_users: int
    active_tasks: int
    queued_tasks: int
    today_income: float
    income_change: float
    total_novels: int
    total_videos: int


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None
    balance: Optional[float] = None


class APIKeyCreate(BaseModel):
    user_id: int
    name: str
    permissions: List[str] = []
    rate_limit: int = 100


class SystemConfigUpdate(BaseModel):
    key: str
    value: dict
    description: Optional[str] = None


# ==================== 1. 数据概览 ====================
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取仪表盘数据"""
    # 用户总数
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar() or 0

    # 今日新增用户
    today = datetime.utcnow().date()
    today_users = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )
    today_new_users = today_users.scalar() or 0

    # 活跃任务数（运行中）
    active_tasks = await db.execute(
        select(func.count(Task.id)).where(
            Task.status.in_(["running", "preparing"])
        )
    )
    active_task_count = active_tasks.scalar() or 0

    # 排队任务数
    queued_tasks = await db.execute(
        select(func.count(Task.id)).where(Task.status == "queued")
    )
    queued_task_count = queued_tasks.scalar() or 0

    # 今日收入
    today_income_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == "success",
            func.date(Payment.paid_at) == today
        )
    )
    today_income = today_income_result.scalar() or 0.0

    # 昨日收入（计算增长率）
    yesterday = today - timedelta(days=1)
    yesterday_income_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == "success",
            func.date(Payment.paid_at) == yesterday
        )
    )
    yesterday_income = yesterday_income_result.scalar() or 0.0
    income_change = ((today_income - yesterday_income) / yesterday_income * 100) if yesterday_income > 0 else 0

    # 作品总数
    novel_count = await db.execute(select(func.count(Novel.id)))
    total_novels = novel_count.scalar() or 0

    video_count = await db.execute(select(func.count(Video.id)))
    total_videos = video_count.scalar() or 0

    return DashboardStats(
        total_users=total_users,
        today_new_users=today_new_users,
        active_tasks=active_task_count,
        queued_tasks=queued_task_count,
        today_income=today_income,
        income_change=income_change,
        total_novels=total_novels,
        total_videos=total_videos
    )


@router.get("/dashboard/income-trend")
async def get_income_trend(
    days: int = 30,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取收入趋势数据（近N天）"""
    result = []
    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=days - i - 1)
        income_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == "success",
                func.date(Payment.paid_at) == date
            )
        )
        income = income_result.scalar() or 0.0
        result.append({
            "date": date.isoformat(),
            "income": float(income)
        })
    return result


@router.get("/dashboard/recent-users")
async def get_recent_users(
    limit: int = 5,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取最近注册用户"""
    result = await db.execute(
        select(User).order_by(desc(User.created_at)).limit(limit)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "subscription_tier": u.subscription_tier,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]


# ==================== 2. 用户管理 ====================
@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    subscription_tier: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    query = select(User)

    # 搜索过滤
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%") if User.phone else False
            )
        )

    # 套餐过滤
    if subscription_tier:
        query = query.where(User.subscription_tier == subscription_tier)

    # 状态过滤
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # 总数
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # 分页查询
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "phone": u.phone,
                "subscription_tier": u.subscription_tier,
                "balance": u.balance,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    }


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 统计用户数据
    task_count = await db.execute(select(func.count(Task.id)).where(Task.user_id == user_id))
    novel_count = await db.execute(select(func.count(Novel.id)).where(Novel.user_id == user_id))
    video_count = await db.execute(select(func.count(Video.id)).where(Video.user_id == user_id))

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "subscription_tier": user.subscription_tier,
        "balance": user.balance,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "stats": {
            "total_tasks": task_count.scalar() or 0,
            "total_novels": novel_count.scalar() or 0,
            "total_videos": video_count.scalar() or 0
        }
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.subscription_tier:
        user.subscription_tier = user_update.subscription_tier
    if user_update.balance is not None:
        user.balance = user_update.balance

    await db.commit()
    return {"message": "用户信息已更新"}


# ==================== 3. 小说管理 ====================
@router.get("/novels")
async def list_novels(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取小说列表"""
    query = select(Novel).join(User)

    if search:
        query = query.where(Novel.title.ilike(f"%{search}%"))
    if category:
        query = query.where(Novel.category == category)
    if is_public is not None:
        query = query.where(Novel.is_public == is_public)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(Novel.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    novels = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "author": n.user.username,
                "category": n.category,
                "genre": n.genre,
                "word_count": n.word_count,
                "is_public": n.is_public,
                "rating": n.rating,
                "view_count": n.view_count,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in novels
        ]
    }


@router.patch("/novels/{novel_id}/status")
async def update_novel_status(
    novel_id: int,
    is_public: bool,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新小说状态（上架/下架）"""
    result = await db.execute(select(Novel).where(Novel.id == novel_id))
    novel = result.scalar_one_or_none()

    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    novel.is_public = is_public
    await db.commit()
    return {"message": "小说状态已更新"}


@router.delete("/novels/{novel_id}")
async def delete_novel(
    novel_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除小说"""
    result = await db.execute(select(Novel).where(Novel.id == novel_id))
    novel = result.scalar_one_or_none()

    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    await db.delete(novel)
    await db.commit()
    return {"message": "小说已删除"}


# ==================== 4. 视频管理 ====================
@router.get("/videos")
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    video_type: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取视频列表"""
    query = select(Video).join(User)

    if search:
        query = query.where(Video.title.ilike(f"%{search}%"))
    if video_type:
        query = query.where(Video.video_type == video_type)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(Video.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    videos = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": v.id,
                "title": v.title,
                "author": v.user.username,
                "video_type": v.video_type,
                "duration": v.duration,
                "episode_count": v.episode_count,
                "is_public": v.is_public,
                "view_count": v.view_count,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in videos
        ]
    }


# ==================== 5. 任务监控 ====================
@router.get("/tasks/stats")
async def get_task_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取任务统计"""
    today = datetime.utcnow().date()

    running = await db.execute(select(func.count(Task.id)).where(Task.status == "running"))
    queued = await db.execute(select(func.count(Task.id)).where(Task.status == "queued"))
    completed_today = await db.execute(
        select(func.count(Task.id)).where(
            Task.status == "completed",
            func.date(Task.completed_at) == today
        )
    )
    failed_today = await db.execute(
        select(func.count(Task.id)).where(
            Task.status == "failed",
            func.date(Task.updated_at) == today
        )
    )

    return {
        "running": running.scalar() or 0,
        "queued": queued.scalar() or 0,
        "completed_today": completed_today.scalar() or 0,
        "failed_today": failed_today.scalar() or 0
    }


@router.get("/tasks")
async def list_tasks(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    query = select(Task).join(User)

    if status_filter:
        query = query.where(Task.status == status_filter)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(Task.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": t.id,
                "user": t.user.username,
                "task_type": t.task_type,
                "status": t.status,
                "progress": t.progress,
                "current_agent": t.current_agent,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "elapsed_time": (datetime.utcnow() - t.created_at).seconds // 60 if t.created_at else 0
            }
            for t in tasks
        ]
    }


@router.post("/tasks/{task_id}/stop")
async def stop_task(
    task_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """停止任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in ["running", "queued"]:
        raise HTTPException(status_code=400, detail="任务无法停止")

    task.status = "cancelled"
    await db.commit()
    return {"message": "任务已停止"}


# ==================== 6. API Key管理 ====================
@router.get("/api-keys")
async def list_api_keys(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取API Key列表"""
    query = select(APIKey).join(User)

    if search:
        query = query.where(
            or_(
                APIKey.name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(APIKey.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    api_keys = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": k.id,
                "user": k.user.username,
                "name": k.name,
                "permissions": k.permissions,
                "rate_limit": k.rate_limit,
                "usage_count": k.usage_count,
                "is_active": k.is_active,
                "created_at": k.created_at.isoformat() if k.created_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None
            }
            for k in api_keys
        ]
    }


@router.post("/api-keys")
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建API Key"""
    from app.core.security import generate_api_key, hash_api_key

    # 验证用户存在
    result = await db.execute(select(User).where(User.id == api_key_data.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成API Key
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)

    # 创建记录
    api_key_record = APIKey(
        user_id=api_key_data.user_id,
        key_hash=key_hash,
        name=api_key_data.name,
        permissions=api_key_data.permissions,
        rate_limit=api_key_data.rate_limit,
        is_active=True
    )

    db.add(api_key_record)
    await db.commit()
    await db.refresh(api_key_record)

    return {
        "message": "API Key创建成功",
        "api_key": api_key,
        "id": api_key_record.id
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """吊销API Key"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key不存在")

    api_key.is_active = False
    await db.commit()
    return {"message": "API Key已吊销"}


# ==================== 7. 财务报表 ====================
@router.get("/finance/summary")
async def get_finance_summary(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取财务汇总"""
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    # 本月总收入
    month_income = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.status == "success",
            Payment.paid_at >= month_start
        )
    )
    total_income = month_income.scalar() or 0.0

    # 本月API成本（模拟数据，实际应从成本表获取）
    api_cost = total_income * 0.764  # 假设成本率76.4%

    # 毛利
    gross_profit = total_income - api_cost

    # 毛利率
    profit_margin = (gross_profit / total_income * 100) if total_income > 0 else 0

    return {
        "month_income": float(total_income),
        "api_cost": float(api_cost),
        "gross_profit": float(gross_profit),
        "profit_margin": float(profit_margin)
    }


@router.get("/finance/trend")
async def get_finance_trend(
    days: int = 30,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取收入成本趋势"""
    result = []
    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=days - i - 1)
        income_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == "success",
                func.date(Payment.paid_at) == date
            )
        )
        income = income_result.scalar() or 0.0
        cost = income * 0.764

        result.append({
            "date": date.isoformat(),
            "income": float(income),
            "cost": float(cost)
        })
    return result


# ==================== 8. 发布管理 ====================
@router.get("/publish")
async def list_publish_records(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取发布记录"""
    query = select(PublishRecord)

    if status_filter:
        query = query.where(PublishRecord.status == status_filter)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(PublishRecord.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": r.id,
                "content_title": r.content_title,
                "content_type": r.content_type,
                "platform": r.platform,
                "status": r.status,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "published_at": r.published_at.isoformat() if r.published_at else None
            }
            for r in records
        ]
    }


@router.post("/publish/{record_id}/retry")
async def retry_publish(
    record_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """重试发布"""
    result = await db.execute(select(PublishRecord).where(PublishRecord.id == record_id))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="发布记录不存在")

    record.status = "pending"
    record.error_message = None
    await db.commit()
    return {"message": "已重新提交发布任务"}


# ==================== 9. 系统日志 ====================
@router.get("/logs")
async def list_logs(
    skip: int = 0,
    limit: int = 50,
    level: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统日志"""
    query = select(SystemLog)

    if level:
        query = query.where(SystemLog.level == level)
    if search:
        query = query.where(SystemLog.message.ilike(f"%{search}%"))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(desc(SystemLog.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": l.id,
                "level": l.level,
                "module": l.module,
                "message": l.message,
                "created_at": l.created_at.isoformat() if l.created_at else None
            }
            for l in logs
        ]
    }


# ==================== 10. 系统配置 ====================
@router.get("/config")
async def get_all_configs(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取所有系统配置"""
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()

    return {
        c.key: {
            "value": c.value,
            "description": c.description,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        }
        for c in configs
    }


@router.get("/config/{key}")
async def get_config(
    key: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取单个配置"""
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    return {
        "key": config.key,
        "value": config.value,
        "description": config.description
    }


@router.put("/config")
async def update_config(
    config_data: SystemConfigUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新系统配置"""
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == config_data.key))
    config = result.scalar_one_or_none()

    if config:
        config.value = config_data.value
        if config_data.description:
            config.description = config_data.description
        config.updated_at = datetime.utcnow()
    else:
        config = SystemConfig(
            key=config_data.key,
            value=config_data.value,
            description=config_data.description
        )
        db.add(config)

    await db.commit()
    return {"message": "配置已更新"}
