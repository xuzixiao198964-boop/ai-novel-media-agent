#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "104.244.90.202"
USER = "root"
PASSWORD = "vDyCuc83NxWw"

def deploy_config():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到服务器 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASSWORD)

        sftp = ssh.open_sftp()

        # 上传config.py
        print("上传config.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\config.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/config.py"
        sftp.put(local_file, remote_file)
        print("✓ config.py上传成功")

        sftp.close()

        # 重启后端服务
        print("\n重启后端服务...")
        commands = [
            "pkill -f 'uvicorn app.main:app' || true",
            "sleep 2",
            "cd /opt/ai-novel-media-agent/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/backend.log 2>&1 &",
            "sleep 3"
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()

        print("✓ 后端服务已重启")

        # 检查服务状态
        print("\n检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        ps_result = stdout.read().decode()

        if ps_result:
            print("✓ 后端服务运行中")
        else:
            print("✗ 后端服务未运行")
            return

        # 测试API
        import time
        time.sleep(2)
        print("\n测试API...")

        # 登录
        login_cmd = 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\''
        stdin, stdout, stderr = ssh.exec_command(login_cmd)
        login_result = stdout.read().decode()

        import json
        try:
            login_data = json.loads(login_result)
            token = login_data.get('access_token')
            if token:
                print("✓ 登录成功")

                # 测试用户API
                test_cmd = f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/users/profile"
                stdin, stdout, stderr = ssh.exec_command(test_cmd)
                result = stdout.read().decode()
                print(f"✓ 用户资料API: {result[:100]}")

                # 测试支付API
                test_cmd = f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/payments/history"
                stdin, stdout, stderr = ssh.exec_command(test_cmd)
                result = stdout.read().decode()
                print(f"✓ 支付历史API: {result[:100]}")
            else:
                print("✗ 登录失败")
        except:
            print(f"✗ 登录响应解析失败: {login_result[:100]}")

        print("\n✓ 部署完成！")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_config()
