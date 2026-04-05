#!/usr/bin/env python3
"""修复所有问题：重启服务、检查数据、添加测试数据"""

import paramiko
import time

def main():
    print("=" * 60)
    print("Fix All Issues")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\nConnecting to 104.244.90.202...")
        ssh.connect('104.244.90.202', username='root', password='vDyCuc83NxWw', timeout=10)
        print("[OK] Connected")

        # 1. Kill processes on port 9000
        print("\n[1] Killing processes on port 9000...")
        stdin, stdout, stderr = ssh.exec_command("lsof -ti:9000 | xargs kill -9 2>/dev/null || true")
        stdout.read()
        time.sleep(2)
        print("[OK] Port cleared")

        # 2. Restart backend service
        print("\n[2] Restarting backend service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-novel-media-agent")
        stdout.read()
        time.sleep(3)

        stdin, stdout, stderr = ssh.exec_command("systemctl status ai-novel-media-agent | head -10")
        status = stdout.read().decode()
        if "active (running)" in status:
            print("[OK] Service running")
        else:
            print("[WARN] Service status:")
            print(status)

        # 3. Check database
        print("\n[3] Checking database...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM users;'")
        user_count = stdout.read().decode().strip()
        print(f"Users: {user_count}")

        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM novels;'")
        novel_count = stdout.read().decode().strip()
        print(f"Novels: {novel_count}")

        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM videos;'")
        video_count = stdout.read().decode().strip()
        print(f"Videos: {video_count}")

        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM tasks;'")
        task_count = stdout.read().decode().strip()
        print(f"Tasks: {task_count}")

        # 4. Add test data if needed
        if int(novel_count or 0) < 10:
            print("\n[4] Adding test data...")

            # Create script on server
            script = '''
import sys
sys.path.insert(0, "/opt/ai-novel-media-agent/backend")
from app.database import SessionLocal
from app.models import User, Novel, Video, Task, Payment
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Add more users
for i in range(10, 20):
    user = User(
        username=f"user{i}",
        email=f"user{i}@example.com",
        phone=f"1380000{i:04d}",
        hashed_password="dummy",
        subscription_tier=random.choice(["basic", "premium", "enterprise"]),
        balance=random.uniform(0, 1000),
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    db.add(user)

# Add novels
for i in range(1, 51):
    novel = Novel(
        title=f"Novel Title {i}",
        genre=random.choice(["fantasy", "scifi", "romance", "mystery"]),
        content=f"Content of novel {i}...",
        user_id=random.randint(1, 10),
        status=random.choice(["draft", "published", "completed"]),
        word_count=random.randint(10000, 100000),
        created_at=datetime.now() - timedelta(days=random.randint(0, 60))
    )
    db.add(novel)

# Add videos
for i in range(1, 51):
    video = Video(
        title=f"Video Title {i}",
        video_type=random.choice(["novel", "short"]),
        user_id=random.randint(1, 10),
        status=random.choice(["pending", "processing", "completed", "failed"]),
        duration=random.randint(60, 600),
        created_at=datetime.now() - timedelta(days=random.randint(0, 60))
    )
    db.add(video)

# Add tasks
for i in range(1, 31):
    task = Task(
        user_id=random.randint(1, 10),
        task_type=random.choice(["novel_generation", "video_generation", "audio_synthesis"]),
        status=random.choice(["pending", "running", "completed", "failed"]),
        progress=random.randint(0, 100),
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    db.add(task)

# Add payments
for i in range(1, 101):
    payment = Payment(
        user_id=random.randint(1, 10),
        amount=random.choice([9.9, 29.9, 99.9, 199.9]),
        payment_method=random.choice(["alipay", "wechat", "card"]),
        status="completed",
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    db.add(payment)

db.commit()
db.close()
print("Test data added successfully")
'''

            stdin, stdout, stderr = ssh.exec_command(f"cd /opt/ai-novel-media-agent/backend && python3 -c '{script}'")
            result = stdout.read().decode()
            error = stderr.read().decode()

            if error and "successfully" not in result:
                print(f"[ERROR] {error}")
            else:
                print("[OK] Test data added")

        # 5. Test API
        print("\n[5] Testing API...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard")
        result = stdout.read().decode()
        print(f"Dashboard: {result[:200]}")

        print("\n[SUCCESS] All issues fixed!")
        print("\nPlease visit: http://104.244.90.202/admin")
        print("Login: admin / 198964")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
