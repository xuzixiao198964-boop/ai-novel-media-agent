#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Dashboard真实数据并部署"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
REMOTE_DIR = "/opt/ai-novel-media-agent"

def run_ssh_command(ssh, command, description):
    """执行SSH命令"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"{'='*60}")

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print("输出:")
        print(output)
    if error and exit_status != 0:
        print("错误:")
        print(error)

    if exit_status != 0:
        print(f"[X] 命令执行失败，退出码: {exit_status}")
        return False
    else:
        print(f"[OK] 命令执行成功")
        return True

def upload_file(sftp, local_path, remote_path):
    """上传文件"""
    print(f"\n上传文件: {local_path} -> {remote_path}")
    try:
        sftp.put(local_path, remote_path)
        print(f"[OK] 文件上传成功")
        return True
    except Exception as e:
        print(f"[X] 文件上传失败: {e}")
        return False

def main():
    print("="*60)
    print("修复Dashboard真实数据并部署")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接服务器 {SERVER}...")
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
        print("[OK] SSH连接成功")

        sftp = ssh.open_sftp()
        print("[OK] SFTP连接成功")

        # 1. 上传修改后的admin_simple.py
        local_api = "E:/work/ai-novel-media-agent/backend/app/api/admin_simple.py"
        remote_api = f"{REMOTE_DIR}/backend/app/api/admin_simple.py"

        if not upload_file(sftp, local_api, remote_api):
            return False

        # 2. 重启后端服务
        print("\n" + "="*60)
        print("重启后端服务")
        print("="*60)

        # 查找并停止旧进程
        run_ssh_command(ssh,
            "pkill -f 'uvicorn app.main:app'",
            "停止旧的后端进程")

        # 启动新进程
        if not run_ssh_command(ssh,
            f"cd {REMOTE_DIR}/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &",
            "启动后端服务"):
            return False

        # 等待服务启动
        import time
        print("\n等待服务启动...")
        time.sleep(3)

        # 3. 测试API接口
        print("\n" + "="*60)
        print("测试API接口")
        print("="*60)

        tests = [
            ("Dashboard统计", "curl -s http://localhost:9000/api/admin/dashboard"),
            ("收入趋势", "curl -s http://localhost:9000/api/admin/dashboard/income-trend?days=7"),
            ("最近用户", "curl -s http://localhost:9000/api/admin/dashboard/recent-users?limit=3"),
        ]

        all_passed = True
        for test_name, test_cmd in tests:
            stdin, stdout, stderr = ssh.exec_command(test_cmd)
            result = stdout.read().decode('utf-8')
            print(f"\n{test_name}:")
            print(result[:500])  # 只显示前500字符

            if "total_users" in result or "income" in result or "username" in result:
                print(f"[OK] {test_name} 测试通过")
            else:
                print(f"[X] {test_name} 测试失败")
                all_passed = False

        if all_passed:
            print("\n" + "="*60)
            print("[OK] 部署成功!")
            print("="*60)
            print("\n请访问以下地址验证:")
            print(f"管理后台: http://{SERVER}/admin")
            print("\n修复内容:")
            print("1. Dashboard数据概览现在显示真实数据:")
            print("   - 用户总数、今日注册")
            print("   - 活跃任务、排队任务")
            print("   - 今日收入、收入变化")
            print("   - 作品总数（小说+视频）")
            print("2. 收入趋势图显示真实的支付数据")
            print("3. 最近注册用户显示真实用户和套餐信息")
            return True
        else:
            print("\n[X] 部署验证失败")
            return False

    except Exception as e:
        print(f"\n[X] 部署过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()
        print("\n连接已关闭")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
