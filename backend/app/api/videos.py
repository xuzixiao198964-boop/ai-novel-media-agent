# -*- coding: utf-8 -*-
"""视频API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from pathlib import Path

from app.database import get_db
from app.models import User, Video
from app.api.auth import get_current_user

router = APIRouter()


@router.get("")
def list_videos(
    skip: int = 0,
    limit: int = 20,
    source_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取视频列表"""
    query = db.query(Video).filter(Video.user_id == current_user.id)

    if source_type:
        query = query.filter(Video.source_type == source_type)

    videos = query.order_by(desc(Video.created_at)).offset(skip).limit(limit).all()

    return {"total": len(videos), "items": videos}


@router.get("/{video_id}")
def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取视频详情"""
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    return video


@router.get("/{video_id}/download")
def download_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载视频文件"""
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    if not video.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频文件不存在"
        )

    file_path = Path(video.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频文件不存在"
        )

    return FileResponse(
        path=str(file_path),
        filename=f"{video.title}.mp4",
        media_type="video/mp4"
    )


@router.patch("/{video_id}/publish")
def publish_to_square(
    video_id: int,
    is_public: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布/取消发布到广场"""
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    video.is_public = is_public
    db.commit()

    return {"message": "发布状态已更新", "is_public": is_public}


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除视频"""
    video = db.query(Video).filter(
        Video.id == video_id,
        Video.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )

    # 删除文件
    if video.file_path:
        file_path = Path(video.file_path)
        if file_path.exists():
            file_path.unlink()

    db.delete(video)
    db.commit()

    return {"message": "视频已删除"}
