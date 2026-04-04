# -*- coding: utf-8 -*-
"""小说API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db
from app.models import User, Novel
from app.api.auth import get_current_user
from pathlib import Path

router = APIRouter()


@router.get("")
def list_novels(
    skip: int = 0,
    limit: int = 20,
    genre: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取小说列表"""
    query = db.query(Novel).filter(Novel.user_id == current_user.id)

    if genre:
        query = query.filter(Novel.genre == genre)

    if is_public is not None:
        query = query.filter(Novel.is_public == is_public)

    novels = query.order_by(desc(Novel.created_at)).offset(skip).limit(limit).all()

    return {"total": len(novels), "items": novels}


@router.get("/{novel_id}")
def get_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取小说详情"""
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()

    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    return novel


@router.get("/{novel_id}/download")
def download_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载小说文件"""
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()

    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    if not novel.content_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说文件不存在"
        )

    file_path = Path(novel.content_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说文件不存在"
        )

    return FileResponse(
        path=str(file_path),
        filename=f"{novel.title}.md",
        media_type="text/markdown"
    )


@router.patch("/{novel_id}/publish")
def publish_to_square(
    novel_id: int,
    is_public: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布/取消发布到广场"""
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()

    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    novel.is_public = is_public
    db.commit()

    return {"message": "发布状态已更新", "is_public": is_public}


@router.delete("/{novel_id}")
def delete_novel(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除小说"""
    novel = db.query(Novel).filter(
        Novel.id == novel_id,
        Novel.user_id == current_user.id
    ).first()

    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )

    # 删除文件
    if novel.content_path:
        file_path = Path(novel.content_path)
        if file_path.exists():
            file_path.unlink()

    db.delete(novel)
    db.commit()

    return {"message": "小说已删除"}


@router.get("/square/list")
def list_public_novels(
    skip: int = 0,
    limit: int = 20,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取广场公开小说列表"""
    query = db.query(Novel).filter(Novel.is_public == True)

    if genre:
        query = query.filter(Novel.genre == genre)

    novels = query.order_by(desc(Novel.rating), desc(Novel.view_count)).offset(skip).limit(limit).all()

    return {"total": len(novels), "items": novels}
