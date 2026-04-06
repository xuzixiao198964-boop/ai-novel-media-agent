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

        # 1. 测试登录获取token
        print("\n1. 测试登录...")
        login_cmd = """curl -s -X POST http://localhost:9000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"198964"}'"""

        stdin, stdout, stderr = ssh.exec_command(login_cmd)
        login_result = stdout.read().decode()
        print(f"登录结果: {login_result[:200]}")

        try:
            login_data = json.loads(login_result)
            token = login_data.get('access_token')
            if token:
                print(f"✓ 登录成功，获取到token")
            else:
                print("✗ 登录失败，未获取到token")
                return
        except:
            print("✗ 登录响应解析失败")
            return

        # 2. 测试用户API
        print("\n2. 测试用户API...")
        user_apis = [
            ("GET /api/users/profile", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/users/profile"),
            ("GET /api/users/balance", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/users/balance"),
        ]

        for name, cmd in user_apis:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode()
            try:
                data = json.loads(result)
                print(f"  ✓ {name}: {json.dumps(data, ensure_ascii=False)[:100]}")
            except:
                print(f"  ✗ {name}: {result[:100]}")

        # 3. 测试支付API
        print("\n3. 测试支付API...")
        payment_apis = [
            ("GET /api/payments/history", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/payments/history"),
            ("GET /api/payments/packages", f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/payments/packages"),
        ]

        for name, cmd in payment_apis:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode()
            try:
                data = json.loads(result)
                print(f"  ✓ {name}: {json.dumps(data, ensure_ascii=False)[:100]}")
            except:
                print(f"  ✗ {name}: {result[:100]}")

        # 4. 测试任务API
        print("\n4. 测试任务API...")
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/tasks")
        result = stdout.read().decode()
        try:
            data = json.loads(result)
            print(f"  ✓ GET /api/tasks: 返回 {len(data)} 个任务")
        except:
            print(f"  ✗ GET /api/tasks: {result[:100]}")

        # 5. 测试小说API
        print("\n5. 测试小说API...")
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/novels")
        result = stdout.read().decode()
        try:
            data = json.loads(result)
            print(f"  ✓ GET /api/novels: 返回 {len(data)} 篇小说")
        except:
            print(f"  ✗ GET /api/novels: {result[:100]}")

        # 6. 测试视频API
        print("\n6. 测试视频API...")
        stdin, stdout, stderr = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://localhost:9000/api/videos")
        result = stdout.read().decode()
        try:
            data = json.loads(result)
            print(f"  ✓ GET /api/videos: 返回 {len(data)} 个视频")
        except:
            print(f"  ✗ GET /api/videos: {result[:100]}")

        # 7. 检查前端访问
        print("\n7. 检查前端访问...")
        frontend_checks = [
            ("用户端", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000"),
            ("管理端", "curl -s -o /dev/null -w '%{http_code}' http://localhost/admin"),
        ]

        for name, cmd in frontend_checks:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            status = stdout.read().decode().strip()
            if status == "200":
                print(f"  ✓ {name}: HTTP {status}")
            else:
                print(f"  ✗ {name}: HTTP {status}")

        print("\n" + "="*60)
        print("验证完成！")
        print("="*60)
        print(f"\n访问地址:")
        print(f"  用户端: http://{HOST}:8000")
        print(f"  管理端: http://{HOST}/admin")
        print(f"  API文档: http://{HOST}:9000/docs")
        print(f"\n登录账号: admin / 198964")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    verify()
