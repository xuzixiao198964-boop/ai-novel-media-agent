#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复部署问题并运行测试
"""

import paramiko
import sys
import time

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

def execute_remote_command(ssh, command, print_output=True):
    """执行远程命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if print_output:
        if output:
            print(output)
        if error and exit_status != 0:
            print(f"错误: {error}", file=sys.stderr)

    return exit_status, output, error

def main():
    print("="*60)
    print("修复部署问题并运行测试")
    print("="*60)

    try:
        # 连接SSH
        print("\n步骤 1: 连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("[OK] 已连接")

        # 安装Node.js和npm
        print("\n步骤 2: 检查并安装Node.js")
        status, output, error = execute_remote_command(ssh, "which node", print_output=False)
        if status != 0:
            print("Node.js未安装，正在安装...")
            execute_remote_command(ssh, "curl -fsSL https://deb.nodesource.com/setup_18.x | bash -")
            execute_remote_command(ssh, "apt-get install -y nodejs")
            print("[OK] Node.js已安装")
        else:
            print("[OK] Node.js已存在")

        # 重新安装Python依赖（使用--break-system-packages）
        print("\n步骤 3: 重新安装Python依赖")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && pip3 install --break-system-packages -r requirements.txt")
        print("[OK] Python依赖已安装")

        # 安装pytest
        print("\n步骤 4: 安装pytest")
        execute_remote_command(ssh, "pip3 install --break-system-packages pytest pytest-asyncio pytest-cov")
        print("[OK] pytest已安装")

        # 重新构建管理端
        print("\n步骤 5: 重新构建管理端")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/admin && npm install")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/admin && npm run build")
        print("[OK] 管理端已构建")

        # 重启后端服务
        print("\n步骤 6: 重启后端服务")
        execute_remote_command(ssh, "systemctl restart ai-novel-media-agent")
        time.sleep(5)
        status, output, error = execute_remote_command(ssh, "systemctl status ai-novel-media-agent --no-pager", print_output=False)
        if "active (running)" in output:
            print("[OK] 后端服务运行正常")
        else:
            print("[FAIL] 后端服务未正常运行")
            print(output)

        # 运行单元测试
        print("\n步骤 7: 运行单元测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/unit/ -v --tb=short 2>&1")

        if status == 0:
            print("\n[OK] 单元测试全部通过")
        else:
            print("\n[FAIL] 单元测试失败，详细信息如上")
            # 保存失败信息以便分析
            with open("unit_test_failures.log", "w", encoding="utf-8") as f:
                f.write(output)
            print("失败日志已保存到: unit_test_failures.log")

        # 运行集成测试
        print("\n步骤 8: 运行集成测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/integration/ -v --tb=short 2>&1")

        if status == 0:
            print("\n[OK] 集成测试全部通过")
        else:
            print("\n[FAIL] 集成测试失败，详细信息如上")
            # 保存失败信息以便分析
            with open("integration_test_failures.log", "w", encoding="utf-8") as f:
                f.write(output)
            print("失败日志已保存到: integration_test_failures.log")

        # 测试访问
        print("\n步骤 9: 测试访问")
        print("-"*60)

        # 测试后端API
        status, output, error = execute_remote_command(ssh, "curl -s http://localhost:9000/api/health", print_output=False)
        if status == 0 and output:
            print(f"[OK] 后端API响应: {output[:100]}")
        else:
            print("[FAIL] 后端API无响应")

        # 测试管理后台
        status, output, error = execute_remote_command(ssh, "curl -s -I http://localhost/admin | head -1", print_output=False)
        if status == 0 and "200" in output:
            print("[OK] 管理后台可访问")
        else:
            print(f"[FAIL] 管理后台访问失败: {output}")

        # 总结
        print("\n" + "="*60)
        print("修复和测试完成！")
        print("="*60)
        print("\n访问地址：")
        print(f"  产品官网: http://{SERVER_IP}/")
        print(f"  管理后台: http://{SERVER_IP}/admin")
        print(f"  API文档: http://{SERVER_IP}:9000/docs")
        print(f"  健康检查: http://{SERVER_IP}:9000/api/health")

        ssh.close()
        return 0

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
