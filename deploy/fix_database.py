#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接执行SQL更新"""
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
    ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

    print("[Step 1] Checking current table structure...")
    stdin, stdout, stderr = ssh.exec_command("""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "\\d novels"
""")
    print(stdout.read().decode())

    print("\n[Step 2] Adding missing columns...")

    # 逐个添加列
    commands = [
        "ALTER TABLE novels ADD COLUMN content_path VARCHAR(500);",
        "ALTER TABLE novels ADD COLUMN is_public BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE novels ADD COLUMN rating FLOAT DEFAULT 0.0;",
        "ALTER TABLE novels ADD COLUMN view_count INTEGER DEFAULT 0;",
    ]

    for cmd in commands:
        print(f"  Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(f"""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "{cmd}"
""")
        output = stdout.read().decode()
        error = stderr.read().decode()

        if "ERROR" in error:
            if "already exists" in error:
                print(f"    [SKIP] Column already exists")
            else:
                print(f"    [ERROR] {error}")
        else:
            print(f"    [OK] {output.strip()}")

    print("\n[Step 3] Verifying table structure...")
    stdin, stdout, stderr = ssh.exec_command("""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "\\d novels"
""")
    print(stdout.read().decode())

    print("\n[Step 4] Creating videos table...")
    stdin, stdout, stderr = ssh.exec_command("""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "
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
);"
""")
    output = stdout.read().decode()
    error = stderr.read().decode()

    if "ERROR" in error and "already exists" not in error:
        print(f"[ERROR] {error}")
    else:
        print("[OK] Videos table ready")

    print("\n[SUCCESS] Database schema updated!")

finally:
    ssh.close()
