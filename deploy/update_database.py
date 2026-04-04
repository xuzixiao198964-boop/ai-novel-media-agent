#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新数据库表结构"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("[Deploy] Updating database schema...")
    ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

    # 执行SQL更新
    sql_commands = """
-- 更新novels表
ALTER TABLE novels ADD COLUMN IF NOT EXISTS content_path VARCHAR(500);
ALTER TABLE novels ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
ALTER TABLE novels ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0;
ALTER TABLE novels ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;

-- 创建videos表（如果不存在）
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    source_type VARCHAR(50),
    file_path VARCHAR(500),
    thumbnail_path VARCHAR(500),
    duration INTEGER,
    status VARCHAR(20) DEFAULT 'draft',
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

    print("[Step 1] Executing SQL commands...")
    command = f"""
export PGPASSWORD='Aa112211'
psql -h localhost -U ai_novel -d ai_novel_db << 'EOF'
{sql_commands}
EOF
"""

    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()

    print(output)
    if error and "ERROR" in error:
        print(f"[ERROR] {error}")
    else:
        print("[OK] Database schema updated")

    # 重启后端
    print("[Step 2] Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command("pkill -f 'uvicorn.*9000'")
    stdout.channel.recv_exit_status()

    command = """
cd /opt/ai-novel-media-agent/backend && \
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/ai-novel-backend.log 2>&1 &
"""
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout.channel.recv_exit_status()

    import time
    time.sleep(3)

    print("[OK] Backend restarted")

    # 测试
    print("[Step 3] Testing API...")
    import requests

    # 登录获取token
    login_resp = requests.post("http://104.244.90.202/api/auth/login",
                              json={"username": "15606537209", "password": "198964"})
    token = login_resp.json().get("access_token")

    # 测试novels接口
    response = requests.get("http://104.244.90.202/api/novels",
                           headers={"Authorization": f"Bearer {token}"},
                           timeout=10)
    print(f"  Novels API: {response.status_code}")

    # 测试videos接口
    response = requests.get("http://104.244.90.202/api/videos",
                           headers={"Authorization": f"Bearer {token}"},
                           timeout=10)
    print(f"  Videos API: {response.status_code}")

    print("\n[SUCCESS] Database updated!")

finally:
    ssh.close()
