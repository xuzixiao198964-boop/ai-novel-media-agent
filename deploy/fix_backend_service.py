#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查后端启动状态并修复"""

import paramiko
import sys
import io
import time

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
    print("检查并修复后端服务")
    print("=" * 70)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 1. 检查当前状态
        print("\n【1】检查当前状态")
        print("-" * 70)
        check_status = """
echo "进程状态:"
ps aux | grep '[u]vicorn' || echo "无uvicorn进程"

echo ""
echo "端口状态:"
netstat -tlnp 2>/dev/null | grep 9000 || echo "9000端口未监听"
"""
        status, output, error = execute_ssh_command(ssh, check_status)
        print(output)

        # 2. 启动后端服务
        print("\n【2】启动后端服务")
        print("-" * 70)
        start_backend = """
cd /opt/ai-novel-media-agent/backend

# 确保日志目录存在
mkdir -p logs

# 启动服务
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > logs/app.log 2>&1 &

# 等待启动
sleep 5

echo "进程状态:"
ps aux | grep '[u]vicorn'

echo ""
echo "端口状态:"
netstat -tlnp 2>/dev/null | grep 9000
"""
        status, output, error = execute_ssh_command(ssh, start_backend)
        print(output)

        # 3. 检查启动日志
        print("\n【3】检查启动日志")
        print("-" * 70)
        check_log = """
echo "最近的日志:"
tail -30 /opt/ai-novel-media-agent/backend/logs/app.log
"""
        status, output, error = execute_ssh_command(ssh, check_log)
        print(output)

        # 4. 测试API
        print("\n【4】测试API")
        print("-" * 70)
        test_api = """
echo "健康检查:"
curl -s http://localhost:9000/api/health

echo ""
echo ""
echo "Dashboard API:"
curl -s http://localhost:9000/api/admin/dashboard | python3 -m json.tool

echo ""
echo "最近用户API:"
curl -s http://localhost:9000/api/admin/dashboard/recent-users?limit=5 | python3 -m json.tool
"""
        status, output, error = execute_ssh_command(ssh, test_api)
        print(output)

        # 5. 测试前端访问
        print("\n【5】测试前端访问")
        print("-" * 70)
        test_frontend = """
echo "管理后台:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost/admin/

echo ""
echo "API文档:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:9000/docs
"""
        status, output, error = execute_ssh_command(ssh, test_frontend)
        print(output)

        ssh.close()

        print("\n" + "=" * 70)
        print("检查完成")
        print("=" * 70)
        print("\n如果API正常返回数据，说明服务已恢复")
        print("访问地址: http://104.244.90.202/admin")
        print("登录账号: admin / 198964")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
