#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整验证所有功能"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://104.244.90.202:9000"
ADMIN_URL = "http://104.244.90.202/admin"

def test_api(method, endpoint, data=None, description="", expect_status=200):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)

        success = response.status_code == expect_status
        status_icon = "✓" if success else "✗"

        return {
            "description": description,
            "method": method,
            "endpoint": endpoint,
            "status_code": response.status_code,
            "success": success,
            "icon": status_icon
        }

    except Exception as e:
        return {
            "description": description,
            "method": method,
            "endpoint": endpoint,
            "status_code": 0,
            "success": False,
            "icon": "✗",
            "error": str(e)
        }

def main():
    print("="*80)
    print("管理后台完整验证报告")
    print("="*80)

    results = []

    print("\n【1. 核心管理接口】")
    tests = [
        ("GET", "/api/admin/dashboard", None, "Dashboard数据概览", 200),
        ("GET", "/api/admin/users", None, "用户列表", 200),
        ("GET", "/api/admin/novels", None, "小说列表", 200),
        ("GET", "/api/admin/videos", None, "视频列表", 200),
        ("GET", "/api/admin/tasks", None, "任务列表", 200),
        ("GET", "/api/admin/api-keys", None, "API密钥列表", 200),
        ("GET", "/api/admin/logs", None, "系统日志", 200),
        ("GET", "/api/admin/publish", None, "发布记录", 200),
    ]

    for method, endpoint, data, desc, expect in tests:
        result = test_api(method, endpoint, data, desc, expect)
        results.append(result)
        print(f"  {result['icon']} {desc}: {result['status_code']}")

    print("\n【2. 数据统计接口】")
    tests = [
        ("GET", "/api/admin/dashboard/task-distribution", None, "任务类型分布", 200),
        ("GET", "/api/admin/dashboard/subscription-distribution", None, "套餐分布", 200),
        ("GET", "/api/admin/dashboard/income-trend", None, "收入趋势", 200),
        ("GET", "/api/admin/dashboard/recent-users", None, "最近用户", 200),
        ("GET", "/api/admin/tasks/stats", None, "任务统计", 200),
        ("GET", "/api/admin/finance/summary", None, "财务汇总", 200),
        ("GET", "/api/admin/finance/trend", None, "财务趋势", 200),
    ]

    for method, endpoint, data, desc, expect in tests:
        result = test_api(method, endpoint, data, desc, expect)
        results.append(result)
        print(f"  {result['icon']} {desc}: {result['status_code']}")

    print("\n【3. 操作接口（POST/PATCH/DELETE）】")
    tests = [
        ("PATCH", "/api/admin/novels/2/status", {"status": "draft"}, "更新小说状态", 200),
        ("PATCH", "/api/admin/videos/2/status", {"status": "draft"}, "更新视频状态", 200),
    ]

    for method, endpoint, data, desc, expect in tests:
        result = test_api(method, endpoint, data, desc, expect)
        results.append(result)
        print(f"  {result['icon']} {desc}: {result['status_code']}")

    print("\n【4. 前端页面访问】")
    try:
        response = requests.get(ADMIN_URL, timeout=10)
        page_size = len(response.text)
        has_root_div = '<div id="root"></div>' in response.text
        has_script = '<script' in response.text

        if response.status_code == 200 and has_root_div and has_script:
            print(f"  ✓ 管理后台首页: {response.status_code} (页面大小: {page_size} bytes)")
            frontend_ok = True
        else:
            print(f"  ✗ 管理后台首页: {response.status_code} (页面大小: {page_size} bytes)")
            print(f"    - 包含root div: {has_root_div}")
            print(f"    - 包含script: {has_script}")
            frontend_ok = False
    except Exception as e:
        print(f"  ✗ 管理后台首页: 访问失败 - {e}")
        frontend_ok = False

    # 统计结果
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nAPI接口测试: {passed}/{total} 通过")
    print(f"前端页面: {'✓ 正常' if frontend_ok else '✗ 异常'}")

    print("\n【失败的接口】")
    failed = [r for r in results if not r['success']]
    if failed:
        for r in failed:
            print(f"  ✗ {r['description']}: {r['method']} {r['endpoint']} - {r['status_code']}")
            if 'error' in r:
                print(f"    错误: {r['error']}")
    else:
        print("  无")

    print("\n【数据库统计】")
    try:
        dashboard = requests.get(f"{BASE_URL}/api/admin/dashboard", timeout=10).json()
        print(f"  - 总用户数: {dashboard.get('total_users', 0)}")
        print(f"  - 总小说数: {dashboard.get('total_novels', 0)}")
        print(f"  - 总视频数: {dashboard.get('total_videos', 0)}")
        print(f"  - 总任务数: {dashboard.get('total_users', 0)}")
        print(f"  - 活跃任务: {dashboard.get('active_tasks', 0)}")
        print(f"  - 今日收入: ¥{dashboard.get('today_income', 0)}")
    except:
        print("  无法获取统计数据")

    print("\n" + "="*80)
    if passed == total and frontend_ok:
        print("✓ 所有功能验证通过！管理后台已完全部署成功！")
        print("="*80)
        print(f"\n访问地址: {ADMIN_URL}")
        print("登录账号: admin / 198964")
        print("         15606537209 / 198964")
        return True
    else:
        print(f"✗ 有 {total - passed} 个接口测试失败")
        print("="*80)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
