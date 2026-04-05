#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试所有新增的API接口"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://104.244.90.202:9000"

def test_api(method, endpoint, data=None, description=""):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"方法: {method} {endpoint}")
    if data:
        print(f"数据: {json.dumps(data, ensure_ascii=False)}")
    print('='*60)

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)

        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

        if response.status_code in [200, 201]:
            print("✓ 测试通过")
            return True
        else:
            print("✗ 测试失败")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def main():
    print("开始测试所有新增的API接口...")

    results = []

    # 1. 测试停止任务接口
    results.append(test_api(
        "POST",
        "/api/admin/tasks/1/stop",
        {},
        "停止任务接口"
    ))

    # 2. 测试更新小说状态接口
    results.append(test_api(
        "PATCH",
        "/api/admin/novels/1/status",
        {"status": "published"},
        "更新小说状态接口"
    ))

    # 3. 测试更新视频状态接口
    results.append(test_api(
        "PATCH",
        "/api/admin/videos/1/status",
        {"status": "published"},
        "更新视频状态接口"
    ))

    # 4. 测试Dashboard接口
    results.append(test_api(
        "GET",
        "/api/admin/dashboard",
        None,
        "Dashboard接口"
    ))

    # 5. 测试任务列表接口
    results.append(test_api(
        "GET",
        "/api/admin/tasks",
        None,
        "任务列表接口"
    ))

    # 6. 测试小说列表接口
    results.append(test_api(
        "GET",
        "/api/admin/novels",
        None,
        "小说列表接口"
    ))

    # 7. 测试视频列表接口
    results.append(test_api(
        "GET",
        "/api/admin/videos",
        None,
        "视频列表接口"
    ))

    # 8. 测试用户列表接口
    results.append(test_api(
        "GET",
        "/api/admin/users",
        None,
        "用户列表接口"
    ))

    # 9. 测试API密钥列表接口
    results.append(test_api(
        "GET",
        "/api/admin/api-keys",
        None,
        "API密钥列表接口"
    ))

    # 10. 测试系统日志接口
    results.append(test_api(
        "GET",
        "/api/admin/logs",
        None,
        "系统日志接口"
    ))

    # 11. 测试发布记录接口
    results.append(test_api(
        "GET",
        "/api/admin/publish",
        None,
        "发布记录接口"
    ))

    # 12. 测试财务汇总接口
    results.append(test_api(
        "GET",
        "/api/admin/finance/summary",
        None,
        "财务汇总接口"
    ))

    # 13. 测试财务趋势接口
    results.append(test_api(
        "GET",
        "/api/admin/finance/trend",
        None,
        "财务趋势接口"
    ))

    # 14. 测试任务分布接口
    results.append(test_api(
        "GET",
        "/api/admin/dashboard/task-distribution",
        None,
        "任务分布接口"
    ))

    # 15. 测试套餐分布接口
    results.append(test_api(
        "GET",
        "/api/admin/dashboard/subscription-distribution",
        None,
        "套餐分布接口"
    ))

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")

    if passed == total:
        print("\n✓ 所有API接口测试通过！")
        return True
    else:
        print(f"\n✗ 有 {total - passed} 个接口测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
