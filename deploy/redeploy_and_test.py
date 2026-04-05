#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新部署修复后的代码并运行完整测试
"""

import paramiko
import sys
import time
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

LOCAL_PACKAGE = Path(__file__).parent.parent / "full-deploy-fixed.tar.gz"

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
    print("重新部署修复后的代码")
    print("="*60)

    if not LOCAL_PACKAGE.exists():
        print(f"错误: 找不到部署包 {LOCAL_PACKAGE}")
        return 1

    try:
        # 连接SSH
        print("\n步骤 1: 连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("[OK] 已连接")

        # 上传修复后的代码
        print("\n步骤 2: 上传修复后的代码")
        sftp = ssh.open_sftp()
        remote_path = "/tmp/full-deploy-fixed.tar.gz"
        sftp.put(str(LOCAL_PACKAGE), remote_path)
        sftp.close()
        print(f"[OK] 已上传")

        # 备份当前代码
        print("\n步骤 3: 备份当前代码")
        execute_remote_command(ssh, "cd /opt && tar -czf ai-novel-media-agent-backup-$(date +%Y%m%d-%H%M%S).tar.gz ai-novel-media-agent/backend/app/ || true")
        print("[OK] 已备份")

        # 解压新代码（只覆盖backend）
        print("\n步骤 4: 更新后端代码")
        execute_remote_command(ssh, "cd /tmp && mkdir -p deploy-temp && cd deploy-temp && tar -xzf /tmp/full-deploy-fixed.tar.gz")
        execute_remote_command(ssh, "cp -r /tmp/deploy-temp/backend/* /opt/ai-novel-media-agent/backend/")
        execute_remote_command(ssh, "rm -rf /tmp/deploy-temp")
        print("[OK] 后端代码已更新")

        # 重启后端服务
        print("\n步骤 5: 重启后端服务")
        execute_remote_command(ssh, "systemctl restart ai-novel-media-agent")
        print("等待服务启动...")
        time.sleep(10)

        # 检查服务状态
        status, output, error = execute_remote_command(ssh, "systemctl status ai-novel-media-agent --no-pager", print_output=False)
        if "active (running)" in output:
            print("[OK] 后端服务运行正常")
        else:
            print("[FAIL] 后端服务未正常运行")
            print(output)
            # 查看详细日志
            print("\n查看错误日志:")
            execute_remote_command(ssh, "journalctl -u ai-novel-media-agent -n 50 --no-pager")
            return 1

        # 测试API
        print("\n步骤 6: 测试API")
        status, output, error = execute_remote_command(ssh, "curl -s http://localhost:9000/api/health", print_output=False)
        if status == 0 and output:
            print(f"[OK] API响应正常: {output[:100]}")
        else:
            print("[FAIL] API无响应")
            return 1

        # 运行单元测试
        print("\n步骤 7: 运行单元测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/unit/ -v --tb=short 2>&1")

        # 保存测试结果
        test_log_path = Path(__file__).parent.parent / "unit_test_results.log"
        with open(test_log_path, "w", encoding="utf-8") as f:
            f.write(output)

        if status == 0:
            print("\n[OK] 单元测试全部通过")
        else:
            print(f"\n[FAIL] 单元测试失败，详细日志: {test_log_path}")

        # 运行集成测试
        print("\n步骤 8: 运行集成测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/integration/ -v --tb=short 2>&1")

        # 保存测试结果
        test_log_path = Path(__file__).parent.parent / "integration_test_results.log"
        with open(test_log_path, "w", encoding="utf-8") as f:
            f.write(output)

        if status == 0:
            print("\n[OK] 集成测试全部通过")
        else:
            print(f"\n[FAIL] 集成测试失败，详细日志: {test_log_path}")

        # 测试所有访问点
        print("\n步骤 9: 测试所有访问点")
        print("-"*60)

        tests = [
            ("产品官网", "curl -s -I http://localhost/ | head -1"),
            ("管理后台", "curl -s -I http://localhost/admin | head -1"),
            ("API健康检查", "curl -s http://localhost:9000/api/health"),
            ("API文档", "curl -s -I http://localhost:9000/docs | head -1"),
        ]

        all_passed = True
        for name, cmd in tests:
            status, output, error = execute_remote_command(ssh, cmd, print_output=False)
            if status == 0 and ("200" in output or "OK" in output or "healthy" in output):
                print(f"[OK] {name}")
            else:
                print(f"[FAIL] {name}: {output[:100]}")
                all_passed = False

        # 总结
        print("\n" + "="*60)
        print("部署和测试完成！")
        print("="*60)
        print("\n访问地址：")
        print(f"  产品官网: http://{SERVER_IP}/")
        print(f"  管理后台: http://{SERVER_IP}/admin")
        print(f"  API文档: http://{SERVER_IP}:9000/docs")
        print(f"  健康检查: http://{SERVER_IP}:9000/api/health")
        print("\n测试日志：")
        print(f"  单元测试: {Path(__file__).parent.parent / 'unit_test_results.log'}")
        print(f"  集成测试: {Path(__file__).parent.parent / 'integration_test_results.log'}")

        ssh.close()
        return 0

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
