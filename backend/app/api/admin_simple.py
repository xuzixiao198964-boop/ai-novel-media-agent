from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task, Novel, Video, APIKey, PublishRecord, SystemLog, Payment, SystemConfig
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Request models
class NovelStatusUpdate(BaseModel):
    status: str

class TaskStopRequest(BaseModel):
    pass

class ConfigUpdate(BaseModel):
    key: str
    value: Dict[str, Any]
    description: str = ""

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """获取仪表盘数据"""
    total_users = db.query(User).count()
    total_tasks = db.query(Task).count()
    total_novels = db.query(Novel).count()
    total_videos = db.query(Video).count()

    # 今日新增
    today = datetime.now().date()
    today_new_users = db.query(User).filter(User.created_at >= today).count()

    # 活跃任务（运行中+排队中）
    active_tasks = db.query(Task).filter(Task.status.in_(["pending", "running"])).count()
    queued_tasks = db.query(Task).filter(Task.status == "pending").count()

    # 今日收入（从支付表统计）
    today_payments = db.query(Payment).filter(
        Payment.created_at >= today,
        Payment.status == "completed"
    ).all()
    today_income = sum(p.amount for p in today_payments)

    # 昨日收入
    yesterday = today - timedelta(days=1)
    yesterday_payments = db.query(Payment).filter(
        Payment.created_at >= yesterday,
        Payment.created_at < today,
        Payment.status == "completed"
    ).all()
    yesterday_income = sum(p.amount for p in yesterday_payments)

    # 收入变化百分比
    income_change = 0
    if yesterday_income > 0:
        income_change = ((today_income - yesterday_income) / yesterday_income) * 100

    return {
        "total_users": total_users,
        "today_new_users": today_new_users,
        "active_tasks": active_tasks,
        "queued_tasks": queued_tasks,
        "today_income": today_income,
        "income_change": income_change,
        "total_novels": total_novels,
        "total_videos": total_videos
    }

@router.get("/dashboard/task-distribution")
def get_task_distribution(db: Session = Depends(get_db)):
    """获取任务类型分布"""
    from sqlalchemy import func
    results = db.query(
        Task.task_type,
        func.count(Task.id).label('count')
    ).group_by(Task.task_type).all()

    type_names = {
        'novel_generation': '小说生成',
        'video_generation': '视频生成',
        'audio_synthesis': '语音合成'
    }

    return [{
        'name': type_names.get(r.task_type, r.task_type),
        'value': r.count
    } for r in results]

@router.get("/dashboard/subscription-distribution")
def get_subscription_distribution(db: Session = Depends(get_db)):
    """获取套餐分布"""
    from sqlalchemy import func
    results = db.query(
        User.subscription_tier,
        func.count(User.id).label('count')
    ).group_by(User.subscription_tier).all()

    tier_names = {
        'basic': '基础版',
        'premium': '高级版',
        'enterprise': '企业版'
    }

    return [{
        'name': tier_names.get(r.subscription_tier, r.subscription_tier),
        'value': r.count
    } for r in results]

@router.get("/dashboard/income-trend")
def get_income_trend(days: int = 30, db: Session = Depends(get_db)):
    """获取收入趋势"""
    result = []
    end_date = datetime.now().date()

    for i in range(days):
        date = end_date - timedelta(days=days-i-1)
        # 查询当天的支付记录
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())

        payments = db.query(Payment).filter(
            Payment.created_at >= day_start,
            Payment.created_at <= day_end,
            Payment.status == "completed"
        ).all()

        income = sum(p.amount for p in payments)

        result.append({
            "date": date.isoformat(),
            "income": float(income),
            "cost": 0.0,
            "profit": float(income)
        })

    return result

@router.get("/dashboard/recent-users")
def get_recent_users(limit: int = 5, db: Session = Depends(get_db)):
    """获取最近注册用户"""
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "subscription_tier": getattr(u, 'subscription_tier', 'basic'),
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]

@router.get("/users")
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "password": "198964",  # 明文密码，所有用户统一为198964
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "is_active": getattr(u, 'is_active', True),
            "balance": getattr(u, 'balance', 0.0),
            "subscription_tier": getattr(u, 'subscription_tier', 'basic')
        } for u in users],
        "total": total
    }

@router.get("/novels")
def get_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取小说列表"""
    total = db.query(Novel).count()
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": n.id,
            "title": n.title,
            "author": n.user.username if n.user else "未知作者",
            "genre": n.genre,
            "category": n.category,
            "status": n.status,
            "word_count": n.word_count,
            "is_public": n.status == "published",
            "rating": 4.5,  # 可以从评分表获取
            "created_at": n.created_at.isoformat() if n.created_at else None
        } for n in novels],
        "total": total
    }

@router.get("/videos")
def get_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取视频列表"""
    total = db.query(Video).count()
    videos = db.query(Video).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": v.id,
            "title": v.title,
            "author": v.user.username if v.user else "未知作者",
            "video_type": "小说类",
            "status": v.status,
            "duration": v.duration or 0,
            "episode_count": 1,
            "is_public": v.status == "published",
            "created_at": v.created_at.isoformat() if v.created_at else None
        } for v in videos],
        "total": total
    }

@router.get("/tasks/stats")
def get_task_stats(db: Session = Depends(get_db)):
    """获取任务统计"""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    running = db.query(Task).filter(Task.status == "running").count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()

    # 今日统计
    today = datetime.now().date()
    completed_today = db.query(Task).filter(
        Task.status == "completed",
        Task.created_at >= today
    ).count()
    failed_today = db.query(Task).filter(
        Task.status == "failed",
        Task.created_at >= today
    ).count()

    return {
        "total": total,
        "pending": pending,
        "running": running,
        "queued": pending,  # 前端期望queued字段
        "completed": completed,
        "failed": failed,
        "completed_today": completed_today,
        "failed_today": failed_today
    }

@router.get("/tasks")
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取任务列表"""
    total = db.query(Task).count()
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": t.id,
            "user": t.user.username if t.user else "未知用户",
            "task_type": t.task_type,
            "type": t.task_type,
            "status": t.status,
            "progress": t.progress,
            "current_agent": t.current_agent,
            "elapsed_time": 0,  # 可以根据created_at计算
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in tasks],
        "total": total
    }

@router.get("/api-keys")
def get_api_keys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取API密钥列表"""
    total = db.query(APIKey).count()
    keys = db.query(APIKey).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": k.id,
            "user": k.user.username if k.user else "未知用户",
            "name": k.name,
            "key": k.key_hash[:20] + "..." if k.key_hash else "",
            "permissions": k.permissions or [],
            "rate_limit": k.rate_limit,
            "usage_count": k.usage_count,
            "is_active": k.is_active,
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None
        } for k in keys],
        "total": total
    }

@router.get("/logs")
def get_logs(skip: int = 0, limit: int = 100, level: str = None, db: Session = Depends(get_db)):
    """获取系统日志"""
    query = db.query(SystemLog)
    if level:
        query = query.filter(SystemLog.level == level)
    total = query.count()
    logs = query.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": l.id,
            "level": l.level,
            "module": l.module,
            "message": l.message,
            "user_id": l.user_id,
            "metadata": l.log_metadata,
            "created_at": l.created_at.isoformat() if l.created_at else None
        } for l in logs],
        "total": total
    }

@router.get("/finance/summary")
def get_finance_summary(db: Session = Depends(get_db)):
    """获取财务汇总"""
    # 获取本月收入
    today = datetime.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_income = db.query(Payment).filter(
        Payment.created_at >= month_start,
        Payment.status == "completed"
    ).count() * 100.0  # 假设每笔100元

    # 计算API成本（基于任务数量）
    month_tasks = db.query(Task).filter(Task.created_at >= month_start).count()
    api_cost = month_tasks * 2.0  # 假设每个任务成本2元

    gross_profit = month_income - api_cost
    profit_margin = (gross_profit / month_income * 100) if month_income > 0 else 0

    return {
        "month_income": month_income,
        "api_cost": api_cost,
        "gross_profit": gross_profit,
        "profit_margin": round(profit_margin, 2)
    }

@router.get("/finance/trend")
def get_finance_trend(days: int = 30, db: Session = Depends(get_db)):
    """获取财务趋势"""
    result = []
    for i in range(days):
        date = datetime.now().date() - timedelta(days=days-i-1)
        date_start = datetime.combine(date, datetime.min.time())
        date_end = datetime.combine(date, datetime.max.time())

        # 计算当天收入
        daily_income = db.query(Payment).filter(
            Payment.created_at >= date_start,
            Payment.created_at <= date_end,
            Payment.status == "completed"
        ).count() * 100.0

        # 计算当天成本
        daily_tasks = db.query(Task).filter(
            Task.created_at >= date_start,
            Task.created_at <= date_end
        ).count()
        daily_cost = daily_tasks * 2.0

        result.append({
            "date": date.isoformat(),
            "income": daily_income,
            "cost": daily_cost,
            "profit": daily_income - daily_cost
        })
    return result

@router.get("/publish")
def get_publish_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取发布记录"""
    total = db.query(PublishRecord).count()
    records = db.query(PublishRecord).order_by(PublishRecord.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "items": [{
            "id": r.id,
            "content_type": r.content_type,
            "content_title": r.content_title,
            "platform": r.platform,
            "status": r.status,
            "platform_id": r.platform_id,
            "error_message": r.error_message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "published_at": r.published_at.isoformat() if r.published_at else None
        } for r in records],
        "total": total
    }

@router.get("/config")
def get_config(db: Session = Depends(get_db)):
    """获取系统配置"""
    configs = db.query(SystemConfig).all()
    result = {}
    for config in configs:
        result[config.key] = {
            "value": config.value,
            "description": config.description,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }

    # 如果没有配置，返回默认值
    if not result:
        result = {
            "pricing": {
                "value": {
                    "basic": {"novel": 0.05, "video": 0},
                    "advanced": {"novel": 0.08, "video": 0.15},
                    "professional": {"novel": 0.10, "video": 0.20},
                    "enterprise": {"novel": 0, "video": 0}
                },
                "description": "套餐定价配置"
            },
            "system_params": {
                "value": {
                    "billing_multiplier_min": 1.1,
                    "billing_multiplier_max": 1.2,
                    "max_concurrent_tasks": 20,
                    "publish_mode": "mock"
                },
                "description": "系统参数配置"
            },
            "api_keys": {
                "value": {
                    "openai_api_key": "",
                    "openai_base_url": "https://api.openai.com/v1",
                    "video_api_key": "",
                    "video_api_url": "",
                    "tts_api_key": "",
                    "tts_api_url": "",
                    "image_api_key": "",
                    "image_api_url": ""
                },
                "description": "API密钥配置"
            }
        }

    return result

@router.put("/config")
def update_config(config_update: ConfigUpdate, db: Session = Depends(get_db)):
    """更新系统配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == config_update.key).first()

    if config:
        config.value = config_update.value
        config.description = config_update.description
        config.updated_at = datetime.now()
    else:
        config = SystemConfig(
            key=config_update.key,
            value=config_update.value,
            description=config_update.description
        )
        db.add(config)

    db.commit()
    db.refresh(config)

    return {
        "message": "配置已更新",
        "key": config.key,
        "value": config.value
    }

# POST/PATCH/DELETE 接口

@router.post("/tasks/{task_id}/stop")
def stop_task(task_id: int, db: Session = Depends(get_db)):
    """停止任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="只能停止运行中或待处理的任务")

    task.status = "cancelled"
    task.updated_at = datetime.now()
    db.commit()

    return {"message": "任务已停止", "task_id": task_id}

@router.patch("/novels/{novel_id}/status")
def update_novel_status(novel_id: int, update: NovelStatusUpdate, db: Session = Depends(get_db)):
    """更新小说状态"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    novel.status = update.status
    novel.updated_at = datetime.now()
    db.commit()

    return {"message": "小说状态已更新", "novel_id": novel_id, "status": update.status}

@router.delete("/novels/{novel_id}")
def delete_novel(novel_id: int, db: Session = Depends(get_db)):
    """删除小说"""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    db.delete(novel)
    db.commit()

    return {"message": "小说已删除", "novel_id": novel_id}

@router.patch("/videos/{video_id}/status")
def update_video_status(video_id: int, update: NovelStatusUpdate, db: Session = Depends(get_db)):
    """更新视频状态"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    video.status = update.status
    video.updated_at = datetime.now()
    db.commit()

    return {"message": "视频状态已更新", "video_id": video_id, "status": update.status}

@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    """删除视频"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    db.delete(video)
    db.commit()

    return {"message": "视频已删除", "video_id": video_id}

@router.patch("/users/{user_id}/status")
def update_user_status(user_id: int, update: NovelStatusUpdate, db: Session = Depends(get_db)):
    """更新用户状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = (update.status == "active")
    db.commit()

    return {"message": "用户状态已更新", "user_id": user_id, "status": update.status}

@router.delete("/api-keys/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """删除API密钥"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API密钥不存在")

    db.delete(key)
    db.commit()

    return {"message": "API密钥已删除", "key_id": key_id}

