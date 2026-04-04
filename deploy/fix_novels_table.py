#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复novels表"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("104.244.90.202", username="root", password="vDyCuc83NxWw", timeout=30)

    print("[Step 1] Listing all tables...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c '\\dt'"
""")
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(output)
    if error:
        print(f"Error: {error}")

    print("\n[Step 2] Checking novels table structure...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c '\\d novels'"
""")
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(output)
    if error:
        print(f"Error: {error}")

    print("\n[Step 3] Adding missing columns to novels table...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c 'ALTER TABLE novels ADD COLUMN IF NOT EXISTS content_path VARCHAR(500);'"
""")
    print(stdout.read().decode())

    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c 'ALTER TABLE novels ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;'"
""")
    print(stdout.read().decode())

    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c 'ALTER TABLE novels ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0;'"
""")
    print(stdout.read().decode())

    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c 'ALTER TABLE novels ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;'"
""")
    print(stdout.read().decode())

    print("\n[Step 4] Verifying updated structure...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql ai_novel_db -c '\\d novels'"
""")
    print(stdout.read().decode())

    print("\n[SUCCESS] Database updated!")

finally:
    ssh.close()
