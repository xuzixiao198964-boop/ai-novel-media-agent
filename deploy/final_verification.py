#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验证所有功能"""

import paramiko
import json

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def test_api(ssh, name, cmd, check_func):
    """测试API并验证结果"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode()
    try:
        if check_func(result):
            print(f"[PASS] {name}")
            return True
        else:
            print(f"[FAIL] {name}: {result[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False

def main():
    print("="*60)
    print("最终验证报告")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)
        print("[OK] 连接服务器成功\n")

        results = []

        # 1. Dashboard数据概览
        print("[1] Dashboard数据概览")
        results.append(test_api(
            ssh,
            "用户总数 > 0",
            "curl -s http://localhost:9000/api/admin/dashboard",
            lambda r: json.loads(r).get("total_users", 0) > 0
        ))
        results.append(test_api(
            ssh,
            "活跃任务数据",
            "curl -s http://localhost:9000/api/admin/dashboard",
            lambda r: "active_tasks" in r
        ))
        results.append(test_api(
            ssh,
            "今日收入数据",
            "curl -s http://localhost:9000/api/admin/dashboard",
            lambda r: "today_income" in r
        ))
        results.append(test_api(
            ssh,
            "作品总数数据",
            "curl -s http://localhost:9000/api/admin/dashboard",
            lambda r: json.loads(r).get("total_novels", 0) > 0
        ))

        # 2. 任务分布和套餐分布
        print("\n[2] 图表数据")
        results.append(test_api(
            ssh,
            "任务类型分布",
            "curl -s http://localhost:9000/api/admin/dashboard/task-distribution",
            lambda r: len(json.loads(r)) > 0
        ))
        results.append(test_api(
            ssh,
            "套餐分布",
            "curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution",
            lambda r: len(json.loads(r)) > 0
        ))

        # 3. 用户管理
        print("\n[3] 用户管理")
        results.append(test_api(
            ssh,
            "用户列表",
            "curl -s 'http://localhost:9000/api/admin/users?page=1&page_size=10'",
            lambda r: json.loads(r).get("total", 0) > 0
        ))

        # 4. 小说管理
        print("\n[4] 小说管理")
        results.append(test_api(
            ssh,
            "小说列表",
            "curl -s 'http://localhost:9000/api/admin/novels?page=1&page_size=10'",
            lambda r: json.loads(r).get("total", 0) > 0
        ))

        # 5. 视频管理
        print("\n[5] 视频管理")
        results.append(test_api(
            ssh,
            "视频列表",
            "curl -s 'http://localhost:9000/api/admin/videos?page=1&page_size=10'",
            lambda r: json.loads(r).get("total", 0) > 0
        ))

        # 6. 系统配置保存
        print("\n[6] 系统配置")
        results.append(test_api(
            ssh,
            "配置保存API",
            "curl -s -X PUT http://localhost:9000/api/admin/config -H 'Content-Type: application/json' -d '{\"key\":\"api_keys\",\"value\":{\"openai_api_key\":\"test\"},\"description\":\"API密钥配置\"}'",
            lambda r: "配置已更新" in r or "message" in r
        ))

        # 7. 用户端登录
        print("\n[7] 用户端登录")
        login_result = test_api(
            ssh,
            "登录接口",
            "curl -s -X POST http://localhost:9000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"198964\"}'",
            lambda r: "access_token" in r
        )
        results.append(login_result)

        if login_result:
            # 获取token并测试用户资料
            stdin, stdout, stderr = ssh.exec_command(
                "curl -s -X POST http://localhost:9000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"198964\"}'"
            )
            token_data = json.loads(stdout.read().decode())
            token = token_data.get("access_token")

            results.append(test_api(
                ssh,
                "用户资料API",
                f"curl -s http://localhost:9000/api/users/profile -H 'Authorization: Bearer {token}'",
                lambda r: "username" in r
            ))

        # 8. 前端访问
        print("\n[8] 前端访问")
        results.append(test_api(
            ssh,
            "管理端前端",
            "curl -s -I http://localhost/admin/",
            lambda r: "200 OK" in r
        ))
        results.append(test_api(
            ssh,
            "用户端前端",
            "curl -s -I http://localhost:8000/",
            lambda r: "200 OK" in r
        ))

        # 汇总结果
        print("\n" + "="*60)
        print("验证结果汇总")
        print("="*60)
        passed = sum(results)
        total = len(results)
        print(f"\n通过: {passed}/{total}")

        if passed == total:
            print("\n[SUCCESS] 所有验证通过！")
            print("\n可以访问以下地址进行最终确认:")
            print(f"  管理端: http://{SERVER}/admin")
            print(f"  用户端: http://{SERVER}:8000")
            print(f"  登录账号: admin / 198964")
            print("\n请在浏览器中验证:")
            print("  1. Dashboard数据概览显示真实数据（不是0）")
            print("  2. 任务分布饼图清晰可见（高度300px）")
            print("  3. 套餐分布柱状图清晰可见（高度300px）")
            print("  4. 用户管理、小说管理、视频管理显示真实数据")
            print("  5. 系统配置页面底部有API密钥配置")
            print("  6. 可以保存API密钥配置")
            print("  7. 用户端可以登录")
        else:
            print("\n[WARNING] 部分验证失败，请检查上述失败项")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
