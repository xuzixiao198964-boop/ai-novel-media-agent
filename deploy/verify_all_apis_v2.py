#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "104.244.90.202"
USER = "root"
PASSWORD = "vDyCuc83NxWw"

def verify():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到服务器 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASSWORD)

        # 检查后端服务状态
        print("\n检查后端服务...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        ps_result = stdout.read().decode()
        if ps_result:
            print(f"✓ 后端服务运行中")
        else:
            print("✗ 后端服务未运行，正在启动...")
            stdin, stdout, stderr = ssh.exec_command(
                "cd /opt/ai-novel-media-agent/backend && "
                "nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/backend.log 2>&1 &"
            )
            stdout.read()
            import time
            time.sleep(3)

        # 测试健康检查
        print("\n测试健康检查...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/health")
        health = stdout.read().decode()
        print(f"健康检查: {health}")

        # 测试登录
        print("\n测试登录...")
        login_cmd = 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\''
        stdin, stdout, stderr = ssh.exec_command(login_cmd)
        login_result = stdout.read().decode()
        error_result = stderr.read().decode()

        print(f"登录响应: {login_result}")
        if error_result:
            print(f"错误信息: {error_result}")

        if not login_result or login_result.strip() == "":
            print("\n检查后端日志...")
            stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/backend.log")
            log = stdout.read().decode()
            print(f"后端日志:\n{log}")
            return

        try:
            login_data = json.loads(login_result)
            token = login_data.get('access_token')
            if not token:
                print(f"✗ 登录失败: {login_data}")
                return
            print(f"✓ 登录成功")
        except Exception as e:
            print(f"✗ 解析登录响应失败: {e}")
            return

        # 测试各个API
        print("\n测试API端点...")
        apis = [
            ("用户资料", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/users/profile"),
            ("用户余额", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/users/balance"),
            ("支付历史", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/payments/history"),
            ("套餐列表", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/payments/packages"),
            ("任务列表", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/tasks"),
            ("小说列表", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/novels"),
            ("视频列表", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/videos"),
        ]

        results = []
        for name, cmd in apis:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode()
            try:
                data = json.loads(result)
                status = "✓"
                results.append((name, status, "OK"))
                print(f"  {status} {name}: OK")
            except:
                status = "✗"
                results.append((name, status, result[:100]))
                print(f"  {status} {name}: {result[:100]}")

        # 检查前端
        print("\n检查前端访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000")
        status = stdout.read().decode().strip()
        print(f"  用户端 (8000): HTTP {status}")

        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/admin")
        status = stdout.read().decode().strip()
        print(f"  管理端 (80/admin): HTTP {status}")

        print("\n" + "="*60)
        print("验证完成！")
        print("="*60)
        print(f"\n访问地址:")
        print(f"  用户端: http://{HOST}:8000")
        print(f"  管理端: http://{HOST}/admin")
        print(f"  API文档: http://{HOST}:9000/docs")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    verify()
