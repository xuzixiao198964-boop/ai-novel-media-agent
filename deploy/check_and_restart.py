#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import time

def ssh_connect():
    """建立SSH连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    max_retries = 3
    for i in range(max_retries):
        try:
            client.connect('104.244.90.202', username='root', password='8TbXfNYaywmW', timeout=10)
            print(f"[OK] SSH连接成功")
            return client
        except Exception as e:
            print(f"[RETRY {i+1}/{max_retries}] 连接失败: {e}")
            if i < max_retries - 1:
                time.sleep(2)

    raise Exception("SSH连接失败")

def main():
    client = ssh_connect()

    try:
        # 检查服务状态
        print("\n检查后端服务状态...")
        stdin, stdout, stderr = client.exec_command('systemctl status ai-novel-media-backend')
        status = stdout.read().decode('utf-8')
        print(status[:500])

        # 检查main.py是否包含admin_simple路由
        print("\n检查main.py路由注册...")
        stdin, stdout, stderr = client.exec_command('grep -n "admin_simple" /root/ai-novel-media-agent/backend/app/main.py')
        result = stdout.read().decode('utf-8')
        if result:
            print(f"[OK] 找到admin_simple路由:\n{result}")
        else:
            print("[ERROR] 未找到admin_simple路由")

        # 检查admin_simple.py文件
        print("\n检查admin_simple.py文件...")
        stdin, stdout, stderr = client.exec_command('ls -lh /root/ai-novel-media-agent/backend/app/api/admin_simple.py')
        result = stdout.read().decode('utf-8')
        if result:
            print(f"[OK] 文件存在:\n{result}")
        else:
            print("[ERROR] 文件不存在")

        # 重启服务
        print("\n重启后端服务...")
        stdin, stdout, stderr = client.exec_command('systemctl restart ai-novel-media-backend')
        time.sleep(3)

        # 再次检查状态
        print("\n检查重启后状态...")
        stdin, stdout, stderr = client.exec_command('systemctl status ai-novel-media-backend')
        status = stdout.read().decode('utf-8')
        if 'active (running)' in status:
            print("[OK] 服务运行正常")
        else:
            print("[ERROR] 服务未正常运行")
            print(status[:500])

        # 检查日志
        print("\n查看最新日志...")
        stdin, stdout, stderr = client.exec_command('journalctl -u ai-novel-media-backend -n 20 --no-pager')
        logs = stdout.read().decode('utf-8')
        print(logs)

    finally:
        client.close()

if __name__ == '__main__':
    main()
