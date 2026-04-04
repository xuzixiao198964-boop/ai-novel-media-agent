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

# 发布管理
@router.get("/publish/records")
def get_publish_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取发布记录"""
    return []

