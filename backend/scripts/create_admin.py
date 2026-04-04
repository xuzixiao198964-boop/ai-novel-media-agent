#!/usr/bin/env python3
"""创建管理员账号脚本"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()

    try:
        # 检查是否已存在admin用户
        existing = db.query(User).filter(User.username == 'admin').first()
        if existing:
            print("管理员账号已存在")
            return

        # 创建管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            role='admin',
            subscription_tier='enterprise',
            balance=0.0,
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("✅ 管理员账号创建成功")
        print("用户名: admin")
        print("密码: admin123")
        print("⚠️  请立即修改默认密码！")

    except Exception as e:
        print(f"❌ 创建失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()
