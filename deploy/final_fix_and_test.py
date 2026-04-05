#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复：安装pytest并修复管理后台
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
    print("最终修复和完整测试")
    print("="*60)

    try:
        # 连接SSH
        print("\n步骤 1: 连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("[OK] 已连接")

        # 安装pytest
        print("\n步骤 2: 安装pytest及相关依赖")
        execute_remote_command(ssh, "pip3 install --break-system-packages pytest pytest-asyncio pytest-cov httpx")
        print("[OK] pytest已安装")

        # 检查管理后台构建
        print("\n步骤 3: 检查管理后台")
        status, output, error = execute_remote_command(ssh, "ls -la /opt/ai-novel-media-agent/admin/dist/", print_output=False)
        if "index.html" in output:
            print("[OK] 管理后台构建文件存在")
        else:
            print("[WARN] 管理后台构建文件不存在，重新构建...")
            execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/admin && npm install && npm run build")
            print("[OK] 管理后台已重新构建")

        # 检查Nginx配置
        print("\n步骤 4: 检查Nginx配置")
        status, output, error = execute_remote_command(ssh, "nginx -t", print_output=False)
        if status == 0:
            print("[OK] Nginx配置正确")
            execute_remote_command(ssh, "systemctl reload nginx")
        else:
            print("[FAIL] Nginx配置错误")
            print(output)
            print(error)

        # 运行单元测试
        print("\n步骤 5: 运行单元测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/unit/ -v --tb=short 2>&1")

        # 统计测试结果
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        errors = output.count(" ERROR")

        print(f"\n单元测试结果: {passed} 通过, {failed} 失败, {errors} 错误")

        if status == 0:
            print("[OK] 单元测试全部通过")
        else:
            print("[FAIL] 单元测试有失败")
            # 只显示失败的测试
            lines = output.split('\n')
            print("\n失败的测试:")
            for line in lines:
                if 'FAILED' in line or 'ERROR' in line:
                    print(f"  {line}")

        # 运行集成测试
        print("\n步骤 6: 运行集成测试")
        print("-"*60)
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 -m pytest tests/integration/ -v --tb=short 2>&1")

        # 统计测试结果
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        errors = output.count(" ERROR")

        print(f"\n集成测试结果: {passed} 通过, {failed} 失败, {errors} 错误")

        if status == 0:
            print("[OK] 集成测试全部通过")
        else:
            print("[FAIL] 集成测试有失败")
            # 只显示失败的测试
            lines = output.split('\n')
            print("\n失败的测试:")
            for line in lines:
                if 'FAILED' in line or 'ERROR' in line:
                    print(f"  {line}")

        # 完整的访问测试
        print("\n步骤 7: 完整访问测试")
        print("-"*60)

        tests = [
            ("产品官网", "curl -s -o /dev/null -w '%{http_code}' http://localhost/"),
            ("管理后台", "curl -s -o /dev/null -w '%{http_code}' http://localhost/admin"),
            ("API健康检查", "curl -s http://localhost:9000/api/health"),
            ("API文档", "curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/docs"),
        ]

        all_passed = True
        for name, cmd in tests:
            status, output, error = execute_remote_command(ssh, cmd, print_output=False)
            output = output.strip()
            if status == 0 and (output == "200" or "healthy" in output):
                print(f"[OK] {name}: {output}")
            else:
                print(f"[FAIL] {name}: {output}")
                all_passed = False

        # 外部访问测试
        print("\n步骤 8: 外部访问测试")
        print("-"*60)
        import requests

        external_tests = [
            ("产品官网", f"http://{SERVER_IP}/"),
            ("管理后台", f"http://{SERVER_IP}/admin"),
            ("API健康检查", f"http://{SERVER_IP}:9000/api/health"),
        ]

        for name, url in external_tests:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    print(f"[OK] {name}: {resp.status_code}")
                else:
                    print(f"[FAIL] {name}: {resp.status_code}")
            except Exception as e:
                print(f"[FAIL] {name}: {str(e)[:50]}")

        # 总结
        print("\n" + "="*60)
        print("最终测试完成！")
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
