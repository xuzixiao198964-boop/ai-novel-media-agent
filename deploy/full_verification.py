#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整验证前后端"""

import paramiko
import sys
import io
import json

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
        
        print("=" * 70)
        print("完整验证：前后端登录方式和Dashboard数据")
        print("=" * 70)
        
        # 1. 验证后端auth.py
        print("\n【1】验证后端auth.py - 登录接口")
        stdin, stdout, stderr = ssh.exec_command("grep -A 5 'def login' /opt/ai-novel-media-agent/backend/app/api/auth.py | head -10")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output)
        
        if 'UserLogin' in output and 'username' in output:
            print("✓ 后端支持用户名登录")
        else:
            print("✗ 后端还是邮箱登录")
        
        # 2. 验证用户端Login.tsx源码
        print("\n【2】验证用户端Login.tsx源码")
        stdin, stdout, stderr = ssh.exec_command("grep 'placeholder=' /opt/ai-novel-media-agent/frontend/src/pages/Login.tsx | head -5")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output)
        
        if '请输入用户名' in output:
            print("✓ 用户端源码是用户名登录")
        elif '请输入邮箱' in output:
            print("✗ 用户端源码还是邮箱登录")
        
        # 3. 验证用户端构建产物
        print("\n【3】验证用户端构建产物")
        stdin, stdout, stderr = ssh.exec_command("strings /var/www/frontend/assets/*.js | grep -E '请输入用户名|请输入邮箱' | head -3")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output)
        
        if '请输入用户名' in output:
            print("✓ 用户端构建产物包含'请输入用户名'")
        elif '请输入邮箱' in output:
            print("✗ 用户端构建产物还是'请输入邮箱'，需要重新构建")
        
        # 4. 验证后端Dashboard API
        print("\n【4】验证后端Dashboard API")
        test_api = """
import requests
response = requests.get('http://localhost:9000/api/admin/dashboard')
print(response.text)
"""
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_dash_api.py', 'w') as f:
            f.write(test_api)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_dash_api.py")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        try:
            data = json.loads(output)
            print(f"用户总数: {data['total_users']}")
            print(f"活跃任务: {data['active_tasks']}")
            print(f"排队任务: {data['queued_tasks']}")
            print(f"小说总数: {data['total_novels']}")
            print(f"视频总数: {data['total_videos']}")
            
            if data['total_users'] == 1 and data['active_tasks'] == 0 and data['total_novels'] == 0:
                print("✓ Dashboard API返回真实数据")
            else:
                print("✗ Dashboard API返回数据异常")
        except:
            print(f"✗ API返回格式错误: {output}")
        
        # 5. 验证管理端构建产物
        print("\n【5】验证管理端构建时间")
        stdin, stdout, stderr = ssh.exec_command("stat /var/www/admin/index.html | grep Modify")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        # 6. 测试实际登录
        print("\n【6】测试实际登录功能")
        test_login = """
import requests

# 测试用户名登录
response = requests.post(
    'http://localhost:9000/api/auth/login',
    json={'username': 'admin', 'password': '198964'}
)
print(f"用户名登录: {response.status_code}")
if response.status_code == 200:
    print("✓ 用户名登录成功")
else:
    print(f"✗ 用户名登录失败: {response.text}")

# 测试邮箱登录（应该失败）
response = requests.post(
    'http://localhost:9000/api/auth/login',
    json={'email': 'admin@example.com', 'password': '198964'}
)
print(f"\n邮箱登录: {response.status_code}")
if response.status_code != 200:
    print("✓ 邮箱登录已禁用（正确）")
else:
    print("✗ 邮箱登录还能用（错误）")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_login_method.py', 'w') as f:
            f.write(test_login)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_login_method.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n" + "=" * 70)
        print("验证总结")
        print("=" * 70)
        print("\n如果所有项都显示✓，说明前后端都已正确修改")
        print("如果有✗，我会继续修复")
        
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
