#!/usr/bin/env python3
"""验证所有管理后台页面的API接口"""

import paramiko
import json
import time

def main():
    print("=" * 60)
    print("验证所有管理后台页面")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\n连接服务器 104.244.90.202...")
        ssh.connect('104.244.90.202', username='root', password='vDyCuc83NxWw', timeout=10)
        print("[OK] SSH连接成功")

        # 测试所有API接口
        apis = [
            ("Dashboard - 数据概览", "curl -s http://localhost:9000/api/admin/dashboard"),
            ("Dashboard - 收入趋势", "curl -s http://localhost:9000/api/admin/dashboard/income-trend"),
            ("Dashboard - 最近用户", "curl -s http://localhost:9000/api/admin/dashboard/recent-users"),
            ("用户管理 - 列表", "curl -s 'http://localhost:9000/api/admin/users?page=1&page_size=10'"),
            ("小说管理 - 列表", "curl -s 'http://localhost:9000/api/admin/novels?page=1&page_size=10'"),
            ("视频管理 - 列表", "curl -s 'http://localhost:9000/api/admin/videos?page=1&page_size=10'"),
            ("任务监控 - 列表", "curl -s 'http://localhost:9000/api/admin/tasks?page=1&page_size=10'"),
            ("API密钥 - 列表", "curl -s 'http://localhost:9000/api/admin/api-keys?page=1&page_size=10'"),
            ("财务管理 - 支付列表", "curl -s 'http://localhost:9000/api/admin/payments?page=1&page_size=10'"),
            ("发布管理 - 列表", "curl -s 'http://localhost:9000/api/admin/publish?page=1&page_size=10'"),
            ("系统日志 - 列表", "curl -s 'http://localhost:9000/api/admin/logs?page=1&page_size=10'"),
            ("系统配置 - 获取", "curl -s http://localhost:9000/api/admin/config"),
        ]

        results = []
        for name, cmd in apis:
            print(f"\n[{len(results)+1}/{len(apis)}] 测试: {name}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                print(f"[FAIL] {error[:200]}")
                results.append((name, False, error[:200]))
            else:
                try:
                    data = json.loads(output)
                    print(f"[OK] 返回数据: {str(data)[:100]}...")
                    results.append((name, True, ""))
                except:
                    print(f"[FAIL] 无效的JSON: {output[:200]}")
                    results.append((name, False, output[:200]))

        # 测试前端访问
        print("\n" + "=" * 60)
        print("测试前端页面访问")
        print("=" * 60)

        pages = [
            ("管理后台首页", "curl -s -I http://localhost/admin/"),
            ("API文档", "curl -s -I http://localhost:9000/docs"),
            ("健康检查", "curl -s http://localhost:9000/api/health"),
        ]

        for name, cmd in pages:
            print(f"\n测试: {name}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            if "200 OK" in output or "healthy" in output:
                print(f"[OK] {output.split(chr(10))[0]}")
                results.append((name, True, ""))
            else:
                print(f"[FAIL] {output[:200]}")
                results.append((name, False, output[:200]))

        # 汇总结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        print(f"\n总计: {passed}/{total} 通过")

        if passed < total:
            print("\n失败的测试:")
            for name, success, error in results:
                if not success:
                    print(f"  - {name}: {error}")
        else:
            print("\n[SUCCESS] 所有测试通过!")
            print("\n可以访问以下地址:")
            print("  - 管理后台: http://104.244.90.202/admin")
            print("  - 登录账号: admin / 198964")
            print("  - API文档: http://104.244.90.202:9000/docs")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()
        print("\n连接已关闭")

if __name__ == "__main__":
    main()
