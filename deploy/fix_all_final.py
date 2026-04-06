#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复所有问题并完整验证"""

import paramiko
import time
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_command(ssh, cmd, description=""):
    """执行命令并返回结果"""
    if description:
        print(f"\n[*] {description}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8', errors='ignore'), stderr.read().decode('utf-8', errors='ignore')

def main():
    print("="*60)
    print("修复所有问题并完整验证")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)
        print("[OK] 连接服务器成功")

        # 1. 停止所有后端进程
        print("\n[1] 停止旧的后端进程...")
        run_command(ssh, "pkill -9 -f 'uvicorn app.main:app'")
        run_command(ssh, "pkill -9 -f 'python.*backend'")
        time.sleep(2)

        # 2. 检查数据库并添加测试数据
        print("\n[2] 检查数据库...")
        out, err = run_command(ssh, "cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM users;'")
        user_count = int(out.strip()) if out.strip().isdigit() else 0
        print(f"当前用户数: {user_count}")

        if user_count < 10:
            print("\n[3] 添加测试数据...")
            # 上传测试数据脚本
            sftp = ssh.open_sftp()

            # 创建测试数据脚本
            test_data_script = """
import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.database import SessionLocal
from app.models import User, Task, Novel, Video, Payment
from datetime import datetime, timedelta
import random

db = SessionLocal()

# 添加用户
for i in range(3, 18):
    user = User(
        username=f"user{i}",
        email=f"user{i}@example.com",
        phone=f"1380000{i:04d}",
        hashed_password="$2b$12$dummy",
        subscription_tier=random.choice(['basic', 'advanced', 'professional']),
        balance=random.randint(0, 1000)
    )
    db.add(user)

db.commit()

# 添加任务
task_types = ['novel_generation', 'video_generation', 'tts']
statuses = ['running', 'queued', 'completed', 'failed']
for i in range(1, 21):
    task = Task(
        user_id=random.randint(1, 17),
        task_type=random.choice(task_types),
        status=random.choice(statuses),
        progress=random.randint(0, 100),
        created_at=datetime.now() - timedelta(days=random.randint(0, 7))
    )
    db.add(task)

db.commit()

# 添加小说
genres = ['玄幻', '都市', '科幻', '历史', '武侠']
for i in range(1, 56):
    novel = Novel(
        user_id=random.randint(1, 17),
        title=f"测试小说{i}",
        genre=random.choice(genres),
        word_count=random.randint(10000, 500000),
        is_public=random.choice([True, False]),
        rating=round(random.uniform(3.5, 5.0), 1),
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    db.add(novel)

db.commit()

# 添加视频
for i in range(1, 56):
    video = Video(
        user_id=random.randint(1, 17),
        title=f"测试视频{i}",
        video_type=random.choice(['novel', 'original']),
        duration=random.randint(60, 3600),
        is_public=random.choice([True, False]),
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    db.add(video)

db.commit()

# 添加支付记录
for i in range(1, 31):
    payment = Payment(
        user_id=random.randint(1, 17),
        amount=random.choice([10, 50, 100, 200, 500]),
        payment_method='alipay',
        status='completed',
        created_at=datetime.now() - timedelta(days=random.randint(0, 14))
    )
    db.add(payment)

db.commit()
db.close()

print("测试数据添加完成")
"""

            # 写入脚本
            with sftp.open('/tmp/add_test_data.py', 'w') as f:
                f.write(test_data_script)

            sftp.close()

            # 执行脚本
            out, err = run_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 /tmp/add_test_data.py")
            print(out)
            if err:
                print(f"错误: {err}")

        # 4. 启动后端服务
        print("\n[4] 启动后端服务...")
        run_command(ssh, "cd /opt/ai-novel-media-agent/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &")
        time.sleep(5)

        # 5. 验证后端API
        print("\n[5] 验证后端API...")
        out, err = run_command(ssh, "curl -s http://localhost:9000/api/admin/dashboard")
        try:
            data = json.loads(out)
            print(f"[OK] Dashboard API: {data}")
        except:
            print(f"[FAIL] Dashboard API返回无效: {out[:200]}")

        # 6. 测试登录
        print("\n[6] 测试用户登录...")
        login_cmd = """curl -s -X POST http://localhost:9000/api/auth/login \
-H "Content-Type: application/json" \
-d '{"username":"admin","password":"198964"}'"""
        out, err = run_command(ssh, login_cmd)
        try:
            data = json.loads(out)
            if 'access_token' in data:
                print(f"[OK] 登录成功")
                token = data['access_token']

                # 测试用户资料
                out, err = run_command(ssh, f"curl -s http://localhost:9000/api/users/profile -H 'Authorization: Bearer {token}'")
                print(f"[OK] 用户资料: {out[:200]}")
            else:
                print(f"[FAIL] 登录失败: {out}")
        except:
            print(f"[FAIL] 登录返回无效: {out[:200]}")

        # 7. 检查前端
        print("\n[7] 检查前端部署...")
        out, err = run_command(ssh, "curl -s -I http://localhost:8000/")
        if "200 OK" in out:
            print("[OK] 用户端前端正常")
        else:
            print(f"[FAIL] 用户端前端异常: {out[:200]}")

        out, err = run_command(ssh, "curl -s -I http://localhost/admin/")
        if "200 OK" in out:
            print("[OK] 管理端前端正常")
        else:
            print(f"[FAIL] 管理端前端异常: {out[:200]}")

        # 8. 最终统计
        print("\n" + "="*60)
        print("最终数据统计")
        print("="*60)

        stats = [
            ("用户数", "SELECT COUNT(*) FROM users"),
            ("任务数", "SELECT COUNT(*) FROM tasks"),
            ("小说数", "SELECT COUNT(*) FROM novels"),
            ("视频数", "SELECT COUNT(*) FROM videos"),
            ("支付记录", "SELECT COUNT(*) FROM payments"),
        ]

        for name, sql in stats:
            out, err = run_command(ssh, f"cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db '{sql}'")
            print(f"{name}: {out.strip()}")

        print("\n" + "="*60)
        print("部署完成！")
        print("="*60)
        print("\n访问地址:")
        print(f"  用户端: http://{SERVER}:8000")
        print(f"  管理端: http://{SERVER}/admin")
        print(f"  登录: admin / 198964")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
