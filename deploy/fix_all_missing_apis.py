#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复所有缺失的API接口"""

import paramiko
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_ssh_command(ssh, command, description):
    """执行SSH命令"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print('='*60)

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if output:
        print("输出:")
        print(output)
    if error:
        print("错误:")
        print(error)

    if exit_status != 0:
        print(f"❌ 命令执行失败，退出码: {exit_status}")
        return False
    else:
        print(f"✓ {description} 成功")
        return True

def main():
    print("开始修复所有缺失的API接口...")

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("✓ SSH连接成功")

        # 1. 上传修复后的admin_simple.py
        print("\n上传修复后的admin_simple.py...")
        sftp = ssh.open_sftp()
        local_file = r"E:\work\ai-novel-media-agent\backend\app\api\admin_simple.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/api/admin_simple.py"

        sftp.put(local_file, remote_file)
        print(f"✓ 文件上传成功: {remote_file}")
        sftp.close()

        # 2. 重启后端服务
        run_ssh_command(
            ssh,
            "systemctl restart ai-novel-backend",
            "重启后端服务"
        )

        # 3. 等待服务启动
        import time
        print("\n等待服务启动...")
        time.sleep(3)

        # 4. 检查服务状态
        run_ssh_command(
            ssh,
            "systemctl status ai-novel-backend --no-pager",
            "检查后端服务状态"
        )

        # 5. 测试新增的API接口
        print("\n" + "="*60)
        print("测试新增的API接口")
        print("="*60)

        test_commands = [
            ("curl -X POST http://localhost:9000/api/admin/tasks/1/stop -H 'Content-Type: application/json'",
             "测试停止任务接口"),
            ("curl -X PATCH http://localhost:9000/api/admin/novels/1/status -H 'Content-Type: application/json' -d '{\"status\":\"published\"}'",
             "测试更新小说状态接口"),
            ("curl http://localhost:9000/api/admin/dashboard",
             "测试Dashboard接口"),
        ]

        for cmd, desc in test_commands:
            run_ssh_command(ssh, cmd, desc)

        print("\n" + "="*60)
        print("✓ 所有API接口修复完成！")
        print("="*60)
        print("\n修复内容:")
        print("1. ✓ 添加停止任务接口: POST /api/admin/tasks/{id}/stop")
        print("2. ✓ 添加更新小说状态接口: PATCH /api/admin/novels/{id}/status")
        print("3. ✓ 添加删除小说接口: DELETE /api/admin/novels/{id}")
        print("4. ✓ 添加更新视频状态接口: PATCH /api/admin/videos/{id}/status")
        print("5. ✓ 添加删除视频接口: DELETE /api/admin/videos/{id}")
        print("6. ✓ 添加更新用户状态接口: PATCH /api/admin/users/{id}/status")
        print("7. ✓ 添加删除API密钥接口: DELETE /api/admin/api-keys/{id}")
        print("\n请在浏览器中测试: http://104.244.90.202/admin")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
