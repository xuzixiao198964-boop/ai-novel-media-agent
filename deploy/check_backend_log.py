#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查后端日志"""
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

    print("[1] Checking backend log...")
    stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/ai-novel-backend.log")
    output = stdout.read().decode()
    print(output)

    print("\n[2] Checking if process is running...")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
    output = stdout.read().decode()
    print(output if output else "No process found")

finally:
    ssh.close()
