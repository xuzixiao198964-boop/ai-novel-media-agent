#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

def check_routes():
    """检查API路由是否可用"""
    base_url = "http://104.244.90.202:9000"

    # 先登录获取token
    print("登录获取token...")
    login_data = {"username": "admin", "password": "admin123"}
    try:
        resp = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        if resp.status_code == 200:
            token = resp.json()['access_token']
            print(f"[OK] 登录成功")
        else:
            print(f"[ERROR] 登录失败: {resp.status_code}")
            return
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 测试各个路由
    routes = [
        ("/api/admin/dashboard", "仪表板"),
        ("/api/admin/users", "用户管理"),
        ("/api/admin/novels", "小说管理"),
        ("/api/admin/videos", "视频管理"),
        ("/api/admin/tasks", "任务管理"),
        ("/api/admin/api-keys", "API密钥"),
        ("/api/admin/logs", "系统日志"),
        ("/api/admin/publish", "发布管理"),
        ("/api/admin/reports", "操作报表"),
        ("/api/admin/config", "系统配置"),
    ]

    print("\n检查API路由:")
    print("=" * 60)

    success = 0
    failed = 0

    for route, name in routes:
        try:
            resp = requests.get(f"{base_url}{route}", headers=headers, timeout=10)
            if resp.status_code == 200:
                print(f"[OK] {name}: {route}")
                success += 1
            elif resp.status_code == 404:
                print(f"[404] {name}: {route}")
                failed += 1
            else:
                print(f"[{resp.status_code}] {name}: {route}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"\n结果: {success} 成功, {failed} 失败")

    # 检查OpenAPI文档
    print("\n检查OpenAPI文档中的路由...")
    try:
        resp = requests.get(f"{base_url}/openapi.json", timeout=10)
        if resp.status_code == 200:
            openapi = resp.json()
            paths = openapi.get('paths', {})
            admin_routes = [p for p in paths.keys() if '/admin/' in p]
            print(f"[OK] 找到 {len(admin_routes)} 个管理路由:")
            for route in sorted(admin_routes):
                print(f"  - {route}")
        else:
            print(f"[ERROR] 无法获取OpenAPI文档: {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] 获取OpenAPI文档异常: {e}")

if __name__ == '__main__':
    check_routes()
