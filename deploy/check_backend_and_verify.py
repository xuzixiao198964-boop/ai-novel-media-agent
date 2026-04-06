#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查后端服务并重新验证API"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 70)
    print("检查后端服务并验证API")
    print("=" * 70)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 1. 检查后端服务
        print("\n【1】检查后端服务状态")
        print("-" * 70)
        check_backend = """
echo "进程状态:"
ps aux | grep '[u]vicorn app.main:app'

echo ""
echo "端口监听:"
netstat -tlnp 2>/dev/null | grep 9000

echo ""
echo "测试健康检查:"
curl -s http://localhost:9000/api/health
"""
        status, output, error = execute_ssh_command(ssh, check_backend)
        print(output)
        if error:
            print(f"错误: {error}")

        # 2. 测试Dashboard API
        print("\n【2】测试Dashboard API")
        print("-" * 70)
        test_dashboard = """
echo "测试 /api/admin/dashboard:"
curl -v http://localhost:9000/api/admin/dashboard 2>&1 | head -20

echo ""
echo "测试 /api/admin/dashboard/recent-users:"
curl -v http://localhost:9000/api/admin/dashboard/recent-users?limit=5 2>&1 | head -20
"""
        status, output, error = execute_ssh_command(ssh, test_dashboard)
        print(output)

        # 3. 检查后端日志
        print("\n【3】检查后端日志")
        print("-" * 70)
        check_logs = """
echo "最近的后端日志:"
tail -50 /opt/ai-novel-media-agent/backend/logs/app.log 2>/dev/null || echo "日志文件不存在"

echo ""
echo "检查是否有错误:"
tail -100 /opt/ai-novel-media-agent/backend/logs/app.log 2>/dev/null | grep -i error | tail -10 || echo "无错误日志"
"""
        status, output, error = execute_ssh_command(ssh, check_logs)
        print(output)

        # 4. 重启后端服务
        print("\n【4】重启后端服务")
        print("-" * 70)
        restart_backend = """
echo "停止旧进程..."
pkill -f "uvicorn app.main:app"
sleep 2

echo "启动新进程..."
cd /opt/ai-novel-media-agent/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > logs/app.log 2>&1 &
sleep 3

echo "检查新进程:"
ps aux | grep '[u]vicorn app.main:app'

echo ""
echo "测试健康检查:"
curl -s http://localhost:9000/api/health
"""
        status, output, error = execute_ssh_command(ssh, restart_backend)
        print(output)

        # 5. 再次验证API
        print("\n【5】验证所有API")
        print("-" * 70)
        verify_apis = """
echo "Dashboard统计:"
curl -s http://localhost:9000/api/admin/dashboard

echo ""
echo ""
echo "最近用户:"
curl -s http://localhost:9000/api/admin/dashboard/recent-users?limit=5

echo ""
echo ""
echo "系统配置:"
curl -s http://localhost:9000/api/admin/config

echo ""
echo ""
echo "用户列表:"
curl -s http://localhost:9000/api/admin/users
"""
        status, output, error = execute_ssh_command(ssh, verify_apis)
        print(output)

        ssh.close()

        print("\n" + "=" * 70)
        print("验证完成")
        print("=" * 70)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
