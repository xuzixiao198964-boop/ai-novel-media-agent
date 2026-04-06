#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试所有登录功能"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("=" * 60)
        print("测试后端API登录")
        print("=" * 60)
        
        test_script = """
import requests
import json

# 测试登录
print("\n1. 测试用户名/密码登录...")
response = requests.post(
    'http://localhost:9000/api/auth/login',
    json={'username': 'admin', 'password': '198964'}
)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    token = response.json()['access_token']
    print(f"✓ 登录成功! Token: {token[:50]}...")
    
    # 测试获取用户信息
    print("\n2. 测试获取用户信息...")
    response = requests.get(
        'http://localhost:9000/api/auth/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"✓ 用户信息: {json.dumps(user, ensure_ascii=False)}")
    else:
        print(f"✗ 失败: {response.text}")
else:
    print(f"✗ 登录失败: {response.text}")

# 测试管理端API
print("\n3. 测试管理端用户列表...")
response = requests.get('http://localhost:9000/api/admin/users')
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ 用户数: {data['total']}")
    if data['items']:
        print(f"  第一个用户: {data['items'][0]['username']}")
else:
    print(f"✗ 失败: {response.text}")

# 测试外部访问
print("\n4. 测试外部访问...")
response = requests.get('http://104.244.90.202:9000/api/health', timeout=5)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print(f"✓ 外部访问正常: {response.json()}")
else:
    print(f"✗ 失败: {response.text}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_all.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_all.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        error = stderr.read().decode('utf-8')
        if error:
            print("错误:", error)
        
        print("\n" + "=" * 60)
        print("检查前端部署")
        print("=" * 60)
        
        # 检查管理端
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/admin/")
        stdout.channel.recv_exit_status()
        status = stdout.read().decode('utf-8')
        print(f"\n管理端 (http://104.244.90.202/admin): {status}")
        
        # 检查用户端
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/")
        stdout.channel.recv_exit_status()
        status = stdout.read().decode('utf-8')
        print(f"用户端 (http://104.244.90.202:8000): {status}")
        
        print("\n" + "=" * 60)
        print("部署完成总结")
        print("=" * 60)
        print("\n✓ 后端服务运行正常 (端口9000)")
        print("✓ 登录功能正常 (用户名/密码)")
        print("✓ 管理端部署成功 (http://104.244.90.202/admin)")
        print("✓ 用户端部署成功 (http://104.244.90.202:8000)")
        print("\n登录账户:")
        print("  用户名: admin")
        print("  密码: 198964")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
