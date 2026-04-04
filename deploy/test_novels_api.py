#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试novels接口并查看详细错误"""
import requests

# 登录
login_resp = requests.post("http://104.244.90.202/api/auth/login",
                          json={"username": "15606537209", "password": "198964"})
token = login_resp.json().get("access_token")

# 测试novels接口
print("[Test] Testing novels API...")
response = requests.get("http://104.244.90.202/api/novels",
                       headers={"Authorization": f"Bearer {token}"},
                       timeout=10)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# 检查后端日志
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("104.244.90.202", username="root", password="vDyCuc83NxWw", timeout=30)

stdin, stdout, stderr = ssh.exec_command("tail -30 /var/log/ai-novel-backend.log | grep -A 10 'novels'")
output = stdout.read().decode()
print("\n[Log]")
print(output)

ssh.close()
