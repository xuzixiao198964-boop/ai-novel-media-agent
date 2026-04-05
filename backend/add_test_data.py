import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import APIKey, SystemLog, PublishRecord, Payment
from datetime import datetime, timedelta
import random

def add_test_data():
    db = SessionLocal()

    try:
        # 添加API密钥
        print("添加API密钥...")
        api_keys = [
            APIKey(
                user_id=1,
                key_hash="sk_test_1234567890abcdef1234567890abcdef",
                name="生产环境密钥",
                permissions=["read", "write"],
                rate_limit=1000,
                usage_count=523,
                is_active=True,
                created_at=datetime.now() - timedelta(days=30),
                last_used_at=datetime.now() - timedelta(hours=2)
            ),
            APIKey(
                user_id=1,
                key_hash="sk_test_abcdef1234567890abcdef1234567890",
                name="测试环境密钥",
                permissions=["read"],
                rate_limit=100,
                usage_count=45,
                is_active=True,
                created_at=datetime.now() - timedelta(days=15),
                last_used_at=datetime.now() - timedelta(days=1)
            ),
            APIKey(
                user_id=2,
                key_hash="sk_test_xyz9876543210fedcba9876543210fedc",
                name="开发环境密钥",
                permissions=["read", "write", "admin"],
                rate_limit=500,
                usage_count=0,
                is_active=False,
                created_at=datetime.now() - timedelta(days=60)
            )
        ]

        for key in api_keys:
            existing = db.query(APIKey).filter(APIKey.key_hash == key.key_hash).first()
            if not existing:
                db.add(key)

        # 添加系统日志
        print("添加系统日志...")
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        log_modules = ["auth", "task", "novel", "video", "payment"]
        log_messages = [
            "用户登录成功",
            "任务创建成功",
            "小说生成完成",
            "视频渲染失败",
            "支付处理中",
            "API调用超时",
            "数据库连接异常",
            "缓存更新成功"
        ]

        for i in range(50):
            log = SystemLog(
                level=random.choice(log_levels),
                module=random.choice(log_modules),
                message=random.choice(log_messages),
                user_id=random.randint(1, 7) if random.random() > 0.3 else None,
                log_metadata={"ip": f"192.168.1.{random.randint(1, 255)}", "duration": random.randint(10, 5000)},
                created_at=datetime.now() - timedelta(hours=random.randint(0, 72))
            )
            db.add(log)

        # 添加发布记录
        print("添加发布记录...")
        platforms = ["微信公众号", "今日头条", "知乎", "小红书", "抖音"]
        statuses = ["success", "pending", "failed"]

        for i in range(20):
            record = PublishRecord(
                user_id=random.randint(1, 7),
                content_type=random.choice(["novel", "video"]),
                content_id=random.randint(1, 5),
                content_title=f"测试内容标题{i+1}",
                platform=random.choice(platforms),
                status=random.choice(statuses),
                platform_id=f"platform_{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
                error_message="网络超时" if random.random() > 0.7 else None,
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                published_at=datetime.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.3 else None
            )
            db.add(record)

        # 添加支付记录
        print("添加支付记录...")
        for i in range(30):
            payment = Payment(
                user_id=random.randint(1, 7),
                amount=random.choice([50.0, 100.0, 200.0, 500.0]),
                payment_method=random.choice(["alipay", "wechat", "card"]),
                status=random.choice(["completed", "pending", "failed"]),
                transaction_id=f"txn_{random.randint(100000, 999999)}",
                created_at=datetime.now() - timedelta(days=random.randint(0, 60))
            )
            db.add(payment)

        db.commit()
        print("测试数据添加成功！")

    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()
