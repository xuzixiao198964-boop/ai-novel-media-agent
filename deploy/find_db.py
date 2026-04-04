#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找正确的数据库名称"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("104.244.90.202", username="root", password="vDyCuc83NxWw", timeout=30)

    print("[Step 1] Listing all databases...")
    stdin, stdout, stderr = ssh.exec_command("""
su - postgres -c "psql -l"
""")
    print(stdout.read().decode())

    print("\n[Step 2] Checking backend config...")
    stdin, stdout, stderr = ssh.exec_command("cat /opt/ai-novel-media-agent/backend/.env")
    output = stdout.read().decode()
    if output:
        print(output)
    else:
        print("No .env file found")

    print("\n[Step 3] Checking config.py...")
    stdin, stdout, stderr = ssh.exec_command("cat /opt/ai-novel-media-agent/backend/app/config.py")
    print(stdout.read().decode())

finally:
    ssh.close()
