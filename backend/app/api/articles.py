# -*- coding: utf-8 -*-
"""资讯API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import User, Article, Category
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    """获取资讯分类"""
    result = await db.execute(
        select(Category).where(Category.is_active == True)
    )
    categories = result.scalars().all()

    return {"items": categories}


@router.post("/categories")
async def create_category(
    name: str,
    rss_url: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建资讯分类（需要管理员权限）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    category = Category(
        name=name,
        rss_url=rss_url,
        is_active=True
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.get("")
async def list_articles(
    skip: int = 0,
    limit: int = 20,
    category_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """获取资讯列表"""
    query = select(Article)

    if category_id:
        query = query.where(Article.category_id == category_id)

    query = query.order_by(desc(Article.published_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()

    return {"total": len(articles), "items": articles}


@router.get("/{article_id}")
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取资讯详情"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资讯不存在"
        )

    return article


@router.post("/fetch")
async def fetch_rss(
    category_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """手动触发RSS抓取"""
    # TODO: 实现RSS抓取逻辑
    return {"message": "RSS抓取任务已提交"}
