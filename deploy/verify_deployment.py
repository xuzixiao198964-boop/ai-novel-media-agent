#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署后验证脚本
在服务器上运行，验证所有服务是否正常
"""
import requests
import time
import sys

SERVER_IP = "104.244.90.202"
TIMEOUT = 10

def test_service(name, url, expected_status=200):
    """测试服务是否可访问"""
    try:
        print(f"测试 {name}...", end=" ")
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == expected_status:
            print(f"✓ 成功 (状态码: {response.status_code})")
            return True
        else:
            print(f"✗ 失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ 失败 ({str(e)})")
        return False

def test_api_endpoint(name, url, method="GET", data=None):
    """测试API端点"""
    try:
        print(f"测试 {name}...", end=" ")
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)

        if response.status_code in [200, 201, 422]:  # 422是验证错误，说明API在工作
            print(f"✓ 成功 (状态码: {response.status_code})")
            return True
        else:
            print(f"✗ 失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ 失败 ({str(e)})")
        return False

def main():
    print("=" * 60)
    print("AI 智能内容创作平台 - 部署验证")
    print("=" * 60)
    print()

    results = []

    # 测试产品官网
    print("1. 产品官网 (Port 80)")
    results.append(test_service("官网首页", f"http://{SERVER_IP}/"))
    results.append(test_service("定价页面", f"http://{SERVER_IP}/pricing.html"))
    print()

    # 测试后端API
    print("2. 后端API (Port 9000)")
    results.append(test_service("健康检查", f"http://{SERVER_IP}:9000/api/health"))
    results.append(test_service("API文档", f"http://{SERVER_IP}:9000/docs"))
    results.append(test_api_endpoint("注册接口", f"http://{SERVER_IP}:9000/api/auth/register", "POST", {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456!"
    }))
    print()

    # 测试用户端Web
    print("3. 用户端Web (Port 8000)")
    results.append(test_service("用户端首页", f"http://{SERVER_IP}:8000/"))
    print()

    # 测试管理后台
    print("4. 管理后台 (Port 8001)")
    results.append(test_service("管理后台", f"http://{SERVER_IP}:8001/"))
    print()

    # 统计结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    print()

    if passed == total:
        print("✓ 所有测试通过！部署成功！")
        return 0
    else:
        print("✗ 部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())
