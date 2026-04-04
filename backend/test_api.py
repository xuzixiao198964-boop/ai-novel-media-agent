#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API测试脚本 - 测试完整的用户注册、登录和任务创建流程"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n[1] Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """测试用户注册"""
    print("\n[2] Testing user registration...")
    data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200, data

def test_login(username, password):
    """测试用户登录"""
    print("\n[3] Testing user login...")
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    return response.status_code == 200, result.get("access_token")

def test_get_me(token):
    """测试获取当前用户信息"""
    print("\n[4] Testing get current user...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_create_trend_task(token):
    """测试创建趋势分析任务"""
    print("\n[5] Testing create trend analysis task...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "task_type": "trend_analysis",
        "input_data": {
            "keywords": ["玄幻", "修仙"],
            "platform": "douyin"
        }
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return response.status_code == 200, result.get("id")

def test_create_writer_task(token):
    """测试创建写作任务"""
    print("\n[6] Testing create writer task...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "task_type": "write_chapter",
        "input_data": {
            "title": "第一章 重生归来",
            "outline": "主角重生到十年前，获得系统",
            "style": "爽文",
            "length": 2000
        }
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return response.status_code == 200, result.get("id")

def test_get_tasks(token):
    """测试获取任务列表"""
    print("\n[7] Testing get tasks list...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Found {len(result)} tasks")
    return response.status_code == 200

def test_get_task(token, task_id):
    """测试获取单个任务"""
    print(f"\n[8] Testing get task {task_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Task status: {result.get('status')}")
    print(f"Task type: {result.get('task_type')}")
    return response.status_code == 200

def main():
    print("=" * 60)
    print("AI Novel Media Agent - API Integration Test")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  python -m uvicorn app.main:app --reload")
    print("\nPress Enter to continue...")
    input()

    try:
        # 1. 健康检查
        if not test_health():
            print("\n[FAIL] Health check failed. Is the server running?")
            return 1

        # 2. 注册用户
        success, user_data = test_register()
        if not success:
            print("\n[FAIL] Registration failed")
            return 1

        # 3. 登录
        success, token = test_login(user_data["username"], user_data["password"])
        if not success or not token:
            print("\n[FAIL] Login failed")
            return 1

        # 4. 获取当前用户信息
        if not test_get_me(token):
            print("\n[FAIL] Get current user failed")
            return 1

        # 5. 创建趋势分析任务
        success, trend_task_id = test_create_trend_task(token)
        if not success:
            print("\n[FAIL] Create trend task failed")
            return 1

        # 6. 创建写作任务
        success, writer_task_id = test_create_writer_task(token)
        if not success:
            print("\n[FAIL] Create writer task failed")
            return 1

        # 7. 获取任务列表
        if not test_get_tasks(token):
            print("\n[FAIL] Get tasks list failed")
            return 1

        # 8. 获取单个任务
        if trend_task_id and not test_get_task(token, trend_task_id):
            print("\n[FAIL] Get task failed")
            return 1

        print("\n" + "=" * 60)
        print("[SUCCESS] All API tests passed!")
        print("=" * 60)
        print("\nYour MVP backend is working correctly!")
        print("\nNext steps:")
        print("  1. Integrate real LLM APIs (DeepSeek/OpenAI)")
        print("  2. Add more agents (Planner, Reviser, etc.)")
        print("  3. Implement async task queue")
        print("  4. Build frontend UI")
        return 0

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server. Please start it first:")
        print("  python -m uvicorn app.main:app --reload")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
