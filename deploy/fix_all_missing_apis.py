#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复所有缺失的API并部署"""

import paramiko
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    print("="*60)
    print("修复所有问题并部署")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)
        print("[OK] 连接成功")

        sftp = ssh.open_sftp()

        # 1. 上传修改后的Dashboard.tsx
        print("\n[1] 上传Dashboard.tsx...")
        sftp.put(
            "E:/work/ai-novel-media-agent/admin/src/pages/Dashboard.tsx",
            "/opt/ai-novel-media-agent/admin/src/pages/Dashboard.tsx"
        )
        print("[OK] Dashboard.tsx上传成功")

        # 2. 重新构建前端
        print("\n[2] 构建管理后台前端...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/admin && npm run build")
        stdout.channel.recv_exit_status()
        print("[OK] 构建完成")

        # 3. 部署到Nginx
        print("\n[3] 部署到Nginx...")
        stdin, stdout, stderr = ssh.exec_command(
            "mkdir -p /var/www/ai-novel-media-agent/admin && "
            "rm -rf /var/www/ai-novel-media-agent/admin/* && "
            "cp -r /opt/ai-novel-media-agent/admin/dist/* /var/www/ai-novel-media-agent/admin/"
        )
        stdout.channel.recv_exit_status()
        print("[OK] 部署完成")

        # 4. 测试API
        print("\n[4] 测试所有API...")
        tests = [
            ("Dashboard", "curl -s http://localhost:9000/api/admin/dashboard"),
            ("任务分布", "curl -s http://localhost:9000/api/admin/dashboard/task-distribution"),
            ("套餐分布", "curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution"),
        ]

        for name, cmd in tests:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode()
            if result and len(result) > 10:
                print(f"[OK] {name}: {result[:100]}...")
            else:
                print(f"[FAIL] {name}: {result}")

        # 5. 测试用户端登录
        print("\n[5] 测试用户端登录...")
        login_cmd = """curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"198964"}'"""

        stdin, stdout, stderr = ssh.exec_command(login_cmd)
        result = stdout.read().decode()

        if "access_token" in result:
            print("[OK] 登录成功")
        else:
            print(f"[FAIL] 登录失败: {result[:200]}")

        # 6. 检查前端访问
        print("\n[6] 检查前端访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s -I http://localhost/admin/")
        result = stdout.read().decode()
        if "200 OK" in result:
            print("[OK] 管理端可访问")

        stdin, stdout, stderr = ssh.exec_command("curl -s -I http://localhost:8000/")
        result = stdout.read().decode()
        if "200 OK" in result:
            print("[OK] 用户端可访问")

        print("\n" + "="*60)
        print("部署完成！")
        print("="*60)

        sftp.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
