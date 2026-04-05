from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task, Novel, Video
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """获取仪表盘数据"""
    total_users = db.query(User).count()
    total_tasks = db.query(Task).count()
    total_novels = db.query(Novel).count()
    total_videos = db.query(Video).count()

    # 今日新增
    today = datetime.now().date()
    today_users = db.query(User).filter(User.created_at >= today).count()
    today_tasks = db.query(Task).filter(Task.created_at >= today).count()

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "total_novels": total_novels,
        "total_videos": total_videos,
        "today_users": today_users,
        "today_tasks": today_tasks
    }

@router.get("/users")
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]

@router.get("/novels")
def get_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取小说列表"""
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return [{
        "id": n.id,
        "title": n.title,
        "genre": n.genre,
        "status": n.status,
        "word_count": n.word_count,
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in novels]

@router.get("/videos")
def get_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取视频列表"""
    videos = db.query(Video).offset(skip).limit(limit).all()
    return [{
        "id": v.id,
        "title": v.title,
        "status": v.status,
        "duration": v.duration,
        "created_at": v.created_at.isoformat() if v.created_at else None
    } for v in videos]

@router.get("/tasks/stats")
def get_task_stats(db: Session = Depends(get_db)):
    """获取任务统计"""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    running = db.query(Task).filter(Task.status == "running").count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()

    return {
        "total": total,
        "pending": pending,
        "running": running,
        "completed": completed,
        "failed": failed
    }

@router.get("/tasks")
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取任务列表"""
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return [{
        "id": t.id,
        "type": t.type,
        "status": t.status,
        "progress": t.progress,
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in tasks]

@router.get("/api-keys")
def get_api_keys(db: Session = Depends(get_db)):
    """获取API密钥列表"""
    return []

@router.get("/logs")
def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取系统日志"""
    return []

@router.get("/finance/summary")
def get_finance_summary(db: Session = Depends(get_db)):
    """获取财务汇总"""
    return {
        "month_income": 0.0,
        "api_cost": 0.0,
        "gross_profit": 0.0,
        "profit_margin": 0.0
    }

@router.get("/finance/trend")
def get_finance_trend(days: int = 30, db: Session = Depends(get_db)):
    """获取财务趋势"""
    return []

@router.get("/publish")
def get_publish_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取发布记录"""
    return []

@router.get("/config")
def get_config(db: Session = Depends(get_db)):
    """获取系统配置"""
    return {
        "site_name": "AI小说媒体平台",
        "api_enabled": True,
        "max_concurrent_tasks": 10,
        "storage_path": "/data/storage"
    }

