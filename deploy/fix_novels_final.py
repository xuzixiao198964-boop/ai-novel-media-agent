#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复novels表 - 使用正确的数据库名"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("104.244.90.202", username="root", password="vDyCuc83NxWw", timeout=30)

    print("[Step 1] Checking novels table structure...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_media -c '\\d novels'"
""")
    print(stdout.read().decode())

    print("\n[Step 2] Adding missing columns...")

    commands = [
        "ALTER TABLE novels ADD COLUMN IF NOT EXISTS content_path VARCHAR(500);",
        "ALTER TABLE novels ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE novels ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0;",
        "ALTER TABLE novels ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;",
    ]

    for cmd in commands:
        print(f"  Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(f"""
su - postgres -c "psql ai_novel_media -c '{cmd}'"
""")
        output = stdout.read().decode()
        print(f"    {output.strip()}")

    print("\n[Step 3] Verifying updated structure...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_media -c '\\d novels'"
""")
    print(stdout.read().decode())

    print("\n[Step 4] Creating videos table if not exists...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_media -c 'CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    source_type VARCHAR(50),
    file_path VARCHAR(500),
    thumbnail_path VARCHAR(500),
    duration INTEGER,
    status VARCHAR(20) DEFAULT '\''draft'\'',
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'"
""")
    print(stdout.read().decode())

    print("\n[SUCCESS] Database schema updated!")

finally:
    ssh.close()
