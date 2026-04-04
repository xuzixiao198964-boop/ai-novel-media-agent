#!/usr/bin/env python3
"""测试管理后台所有功能模块"""
import requests
import json

BASE_URL = "http://104.244.90.202:9000"
ADMIN_URL = "http://104.244.90.202:8001"

def test_admin_functions():
    """测试管理后台10个功能模块"""

    print("=" * 60)
    print("管理后台功能测试")
    print("=" * 60)

    # 1. 登录测试
    print("\n[1/10] 测试登录功能...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"  [OK] 登录成功，获取token: {token[:20]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"  [FAIL] 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"  [ERROR] {e}")
        return

    # 2. 仪表盘数据
    print("\n[2/10] 测试仪表盘数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] 获取仪表盘数据成功")
            print(f"    - 用户总数: {data.get('total_users', 0)}")
            print(f"    - 任务总数: {data.get('total_tasks', 0)}")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 3. 用户管理
    print("\n[3/10] 测试用户管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"  [OK] 获取用户列表成功，共 {len(users)} 个用户")
            if users:
                print(f"    - 示例用户: {users[0].get('username')}")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 4. 小说管理
    print("\n[4/10] 测试小说管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/novels", headers=headers)
        if response.status_code == 200:
            novels = response.json()
            print(f"  [OK] 获取小说列表成功，共 {len(novels)} 本小说")
            if novels:
                print(f"    - 示例小说: {novels[0].get('title')}")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 5. 视频管理
    print("\n[5/10] 测试视频管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/videos", headers=headers)
        if response.status_code == 200:
            videos = response.json()
            print(f"  [OK] 获取视频列表成功，共 {len(videos)} 个视频")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 6. 任务管理
    print("\n[6/10] 测试任务管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"  [OK] 获取任务列表成功，共 {len(tasks)} 个任务")
            if tasks:
                print(f"    - 示例任务: {tasks[0].get('task_type')} - {tasks[0].get('status')}")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 7. API密钥管理
    print("\n[7/10] 测试API密钥管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        if response.status_code == 200:
            keys = response.json()
            print(f"  [OK] 获取API密钥列表成功，共 {len(keys)} 个密钥")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 8. 系统日志
    print("\n[8/10] 测试系统日志...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/logs", headers=headers)
        if response.status_code == 200:
            logs = response.json()
            print(f"  [OK] 获取系统日志成功，共 {len(logs)} 条日志")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 9. 发布管理
    print("\n[9/10] 测试发布管理...")
    try:
        response = requests.get(f"{BASE_URL}/api/publish/records", headers=headers)
        if response.status_code == 200:
            records = response.json()
            print(f"  [OK] 获取发布记录成功，共 {len(records)} 条记录")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 10. 财务报表
    print("\n[10/10] 测试财务报表...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/finance/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print(f"  [OK] 获取财务报表成功")
            print(f"    - 本月收入: {summary.get('month_income', 0)}")
            print(f"    - API成本: {summary.get('api_cost', 0)}")
        else:
            print(f"  [FAIL] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 测试前端页面访问
    print("\n" + "=" * 60)
    print("前端页面访问测试")
    print("=" * 60)

    pages = [
        ("产品官网", "http://104.244.90.202/"),
        ("用户端应用", "http://104.244.90.202:8000/"),
        ("管理后台", "http://104.244.90.202:8001/"),
        ("API文档", "http://104.244.90.202:9000/docs"),
    ]

    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {name}: {url}")
            else:
                print(f"  [FAIL] {name}: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n访问地址:")
    print(f"  管理后台: {ADMIN_URL}")
    print(f"  管理员账号: admin / admin123")
    print(f"  测试用户: 15606537209 / 198964")

if __name__ == "__main__":
    test_admin_functions()
