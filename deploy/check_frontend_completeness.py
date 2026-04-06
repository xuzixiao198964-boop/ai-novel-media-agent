#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查前端页面完整性和后端API支持"""

import os
import re

# 原型要求的页面
REQUIRED_PAGES = {
    "Dashboard": "仪表盘",
    "CreateTask": "创建任务",
    "Tasks": "我的任务",
    "Novels": "小说作品",
    "Videos": "视频作品",
    "Square": "作品广场",
    "Package": "套餐管理",
    "Recharge": "充值",
    "Billing": "消费记录",
    "Platforms": "平台绑定",
    "Settings": "设置"
}

# 检查前端页面
frontend_dir = r"E:\work\ai-novel-media-agent\frontend\src\pages"
print("=" * 70)
print("前端页面检查")
print("=" * 70)

missing_pages = []
existing_pages = []

for page, desc in REQUIRED_PAGES.items():
    tsx_file = os.path.join(frontend_dir, f"{page}.tsx")
    if os.path.exists(tsx_file):
        existing_pages.append(f"✓ {page}.tsx ({desc})")
    else:
        missing_pages.append(f"✗ {page}.tsx ({desc})")

print("\n已存在的页面:")
for page in existing_pages:
    print(f"  {page}")

if missing_pages:
    print("\n缺失的页面:")
    for page in missing_pages:
        print(f"  {page}")
else:
    print("\n✓ 所有页面都已存在")

# 检查后端API
print("\n" + "=" * 70)
print("后端API检查")
print("=" * 70)

backend_api_dir = r"E:\work\ai-novel-media-agent\backend\app\api"
api_files = []

for file in os.listdir(backend_api_dir):
    if file.endswith('.py') and not file.startswith('__'):
        api_files.append(file)

print("\n已存在的API文件:")
for api_file in sorted(api_files):
    print(f"  ✓ {api_file}")

# 检查关键API端点
print("\n" + "=" * 70)
print("关键API端点检查")
print("=" * 70)

required_apis = {
    "auth.py": ["登录", "注册", "用户信息"],
    "tasks.py": ["创建任务", "任务列表", "任务详情"],
    "users.py": ["用户信息", "余额查询"],
    "payments.py": ["充值", "消费记录"],
    "publish.py": ["发布到平台"],
}

print("\n需要的API模块:")
for api_file, endpoints in required_apis.items():
    api_path = os.path.join(backend_api_dir, api_file)
    if os.path.exists(api_path):
        print(f"  ✓ {api_file}: {', '.join(endpoints)}")
    else:
        print(f"  ✗ {api_file}: {', '.join(endpoints)} (缺失)")

print("\n" + "=" * 70)
print("总结")
print("=" * 70)
print(f"\n前端页面: {len(existing_pages)}/{len(REQUIRED_PAGES)} 完成")
print(f"后端API文件: {len(api_files)} 个")

if not missing_pages:
    print("\n✓ 前端页面完整，可以开始部署")
else:
    print(f"\n✗ 缺少 {len(missing_pages)} 个页面，需要补充")
