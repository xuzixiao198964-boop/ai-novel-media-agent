#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import os
import time

def main():
    # 创建SSH客户端
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("连接服务器...")
    max_retries = 5
    for i in range(max_retries):
        try:
            client.connect('104.244.90.202', username='root', password='8TbXfNYaywmW', timeout=15)
            print("[OK] SSH连接成功")
            break
        except Exception as e:
            print(f"[RETRY {i+1}/{max_retries}] 连接失败: {e}")
            if i < max_retries - 1:
                time.sleep(3)
            else:
                print("[ERROR] 无法连接到服务器")
                return

    try:
        # 1. 备份当前main.py
        print("\n备份当前文件...")
        stdin, stdout, stderr = client.exec_command(
            'cp /root/ai-novel-media-agent/backend/app/main.py /root/ai-novel-media-agent/backend/app/main.py.bak'
        )
        stdout.channel.recv_exit_status()

        # 2. 上传main.py
        print("上传main.py...")
        sftp = client.open_sftp()
        local_main = 'E:/work/ai-novel-media-agent/backend/app/main.py'
        remote_main = '/root/ai-novel-media-agent/backend/app/main.py'
        sftp.put(local_main, remote_main)
        print("[OK] main.py上传成功")

        # 3. 上传admin_simple.py
        print("上传admin_simple.py...")
        local_admin = 'E:/work/ai-novel-media-agent/backend/app/api/admin_simple.py'
        remote_admin = '/root/ai-novel-media-agent/backend/app/api/admin_simple.py'
        sftp.put(local_admin, remote_admin)
        print("[OK] admin_simple.py上传成功")

        sftp.close()

        # 4. 验证文件
        print("\n验证上传的文件...")
        stdin, stdout, stderr = client.exec_command('grep -c "admin_simple" /root/ai-novel-media-agent/backend/app/main.py')
        count = stdout.read().decode().strip()
        if int(count) >= 2:
            print(f"[OK] main.py包含admin_simple路由 ({count}处)")
        else:
            print(f"[ERROR] main.py未正确更新")
            return

        stdin, stdout, stderr = client.exec_command('ls -lh /root/ai-novel-media-agent/backend/app/api/admin_simple.py')
        result = stdout.read().decode()
        if result:
            print(f"[OK] admin_simple.py文件存在")
        else:
            print("[ERROR] admin_simple.py文件不存在")
            return

        # 5. 重启服务
        print("\n重启后端服务...")
        stdin, stdout, stderr = client.exec_command('systemctl restart ai-novel-media-backend')
        stdout.channel.recv_exit_status()
        print("[OK] 服务重启命令已执行")

        # 等待服务启动
        print("等待服务启动...")
        time.sleep(5)

        # 6. 检查服务状态
        print("\n检查服务状态...")
        stdin, stdout, stderr = client.exec_command('systemctl is-active ai-novel-media-backend')
        status = stdout.read().decode().strip()
        if status == 'active':
            print("[OK] 服务运行正常")
        else:
            print(f"[ERROR] 服务状态: {status}")

            # 查看日志
            print("\n查看错误日志...")
            stdin, stdout, stderr = client.exec_command('journalctl -u ai-novel-media-backend -n 30 --no-pager')
            logs = stdout.read().decode()
            print(logs)
            return

        # 7. 测试API
        print("\n测试API路由...")
        import requests

        # 登录
        login_resp = requests.post(
            'http://104.244.90.202:9000/api/auth/login',
            json={'username': 'admin', 'password': 'admin123'},
            timeout=10
        )
        if login_resp.status_code != 200:
            print(f"[ERROR] 登录失败: {login_resp.status_code}")
            return

        token = login_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # 测试仪表板
        dashboard_resp = requests.get(
            'http://104.244.90.202:9000/api/admin/dashboard',
            headers=headers,
            timeout=10
        )
        if dashboard_resp.status_code == 200:
            print("[OK] 仪表板API正常")
            data = dashboard_resp.json()
            print(f"     用户数: {data.get('total_users', 0)}")
            print(f"     小说数: {data.get('total_novels', 0)}")
        else:
            print(f"[ERROR] 仪表板API失败: {dashboard_resp.status_code}")
            print(f"        响应: {dashboard_resp.text}")

        print("\n[OK] 后端更新完成!")

    except Exception as e:
        print(f"[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == '__main__':
    main()
