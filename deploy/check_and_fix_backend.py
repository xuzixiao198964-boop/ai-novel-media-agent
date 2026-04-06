#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复后端服务"""

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
    print("检查后端服务状态...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 检查进程
        print("\n[1/5] 检查进程状态...")
        check_script = """
ps aux | grep uvicorn | grep -v grep
echo "---"
netstat -tlnp | grep 9000
"""
        status, output, error = execute_ssh_command(ssh, check_script)
        print(output)

        # 检查日志
        print("\n[2/5] 检查错误日志...")
        log_script = """
if [ -f /var/log/ai-novel-backend.log ]; then
    tail -50 /var/log/ai-novel-backend.log
else
    echo "日志文件不存在"
fi
"""
        status, output, error = execute_ssh_command(ssh, log_script)
        print(output)

        # 停止所有相关进程
        print("\n[3/5] 停止所有相关进程...")
        stop_script = """
pkill -f 'uvicorn app.main:app'
sleep 2
ps aux | grep uvicorn | grep -v grep
"""
        status, output, error = execute_ssh_command(ssh, stop_script)
        print(output if output else "所有进程已停止")

        # 重新启动
        print("\n[4/5] 重新启动后端服务...")
        start_script = """
cd /opt/ai-novel-media-agent/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/ai-novel-backend.log 2>&1 &
sleep 5

# 检查进程
ps aux | grep '[u]vicorn app.main:app'

# 检查端口
netstat -tlnp | grep 9000
"""
        status, output, error = execute_ssh_command(ssh, start_script)
        print(output)

        # 测试API
        print("\n[5/5] 测试API接口...")
        time.sleep(2)
        test_script = """
echo "=== 健康检查 ==="
curl -s http://localhost:9000/api/health

echo ""
echo ""
echo "=== Dashboard数据 ==="
curl -s http://localhost:9000/api/admin/dashboard

echo ""
echo ""
echo "=== 配置接口 ==="
curl -s http://localhost:9000/api/admin/config | head -50
"""
        status, output, error = execute_ssh_command(ssh, test_script)
        print(output)

        ssh.close()

        print("\n" + "=" * 60)
        print("服务检查完成")
        print("=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
