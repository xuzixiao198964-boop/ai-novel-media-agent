# -*- coding: utf-8 -*-
"""支付API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import User, Payment
from app.core.deps import get_current_user

router = APIRouter()


@router.post("/recharge")
async def create_recharge(
    amount: float,
    method: str,  # alipay, wechat
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建充值订单"""
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="充值金额必须大于0"
        )

    if method not in ["alipay", "wechat"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的支付方式"
        )

    # 创建支付记录
    import uuid
    payment = Payment(
        user_id=current_user.id,
        amount=amount,
        payment_method=method,
        status="pending",
        transaction_id=f"recharge_{uuid.uuid4().hex[:16]}"
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    # TODO: 调用支付接口生成支付链接/二维码

    return {
        "payment_id": payment.id,
        "transaction_id": payment.transaction_id,
        "amount": payment.amount,
        "method": payment.payment_method,
        "pay_url": "https://example.com/pay",  # 实际支付链接
        "qr_code": "https://example.com/qr"  # 二维码
    }


@router.post("/callback/{method}")
async def payment_callback(
    method: str,
    db: AsyncSession = Depends(get_db)
):
    """支付回调"""
    # TODO: 实现支付宝/微信支付回调验证和处理
    return {"message": "success"}


@router.get("/history")
async def payment_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取支付历史"""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(desc(Payment.created_at))
        .offset(skip)
        .limit(limit)
    )
    payments = result.scalars().all()

    return {"total": len(payments), "items": payments}


@router.get("/packages")
async def get_packages(
    db: AsyncSession = Depends(get_db)
):
    """获取套餐列表"""
    packages = [
        {
            "id": 1,
            "name": "基础版",
            "price": 99.0,
            "duration_days": 30,
            "features": ["每日10次小说生成", "每日5次视频生成", "基础模板"],
            "is_active": True
        },
        {
            "id": 2,
            "name": "专业版",
            "price": 299.0,
            "duration_days": 30,
            "features": ["每日50次小说生成", "每日20次视频生成", "高级模板", "优先处理"],
            "is_active": True
        },
        {
            "id": 3,
            "name": "企业版",
            "price": 999.0,
            "duration_days": 30,
            "features": ["无限小说生成", "无限视频生成", "全部模板", "专属客服"],
            "is_active": True
        }
    ]
    return {"items": packages}

