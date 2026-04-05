#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化数据库并添加测试数据"""

import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.database import init_db
from app.models import User, Novel, Video, Task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from datetime import datetime
import hashlib

print("=== 初始化数据库 ===")
init_db()
print("✓ 数据库表创建完成")

db = SessionLocal()

try:
    print("\n=== 添加测试用户 ===")
    users_data = [
        ('user1', 'user1@example.com', '15800000001'),
        ('user2', 'user2@example.com', '15800000002'),
        ('user3', 'user3@example.com', '15800000003'),
        ('user4', 'user4@example.com', '15800000004'),
        ('user5', 'user5@example.com', '15800000005'),
    ]

    user_ids = []
    for username, email, phone in users_data:
        existing = db.query(User).filter(User.username == username).first()
        if not existing:
            user = User(
                username=username,
                email=email,
                phone=phone,
                hashed_password=hashlib.sha256('password123'.encode()).hexdigest()
            )
            db.add(user)
            db.flush()
            user_ids.append(user.id)
            print(f"✓ 添加用户: {username} (ID: {user.id})")
        else:
            user_ids.append(existing.id)
            print(f"- 用户已存在: {username} (ID: {existing.id})")

    db.commit()

    # 使用第一个用户ID作为默认用户
    default_user_id = user_ids[0] if user_ids else 1

    print("\n=== 添加测试小说 ===")
    novels_data = [
        ('都市修仙传', '都市', 'completed', 150000),
        ('星际争霸录', '科幻', 'in_progress', 80000),
        ('武侠江湖梦', '武侠', 'completed', 200000),
        ('玄幻大陆', '玄幻', 'in_progress', 120000),
        ('悬疑推理案', '悬疑', 'draft', 50000),
    ]

    for i, (title, genre, status, word_count) in enumerate(novels_data):
        existing = db.query(Novel).filter(Novel.title == title).first()
        if not existing:
            novel = Novel(
                user_id=user_ids[i % len(user_ids)],
                title=title,
                genre=genre,
                status=status,
                word_count=word_count
            )
            db.add(novel)
            print(f"✓ 添加小说: {title}")
        else:
            print(f"- 小说已存在: {title}")

    db.commit()

    print("\n=== 添加测试视频 ===")
    videos_data = [
        ('都市修仙传-第1集', 'completed', 300),
        ('都市修仙传-第2集', 'completed', 280),
        ('星际争霸录-预告片', 'in_progress', 60),
        ('武侠江湖梦-片头曲', 'completed', 120),
        ('玄幻大陆-角色介绍', 'processing', 180),
    ]

    for i, (title, status, duration) in enumerate(videos_data):
        existing = db.query(Video).filter(Video.title == title).first()
        if not existing:
            video = Video(
                user_id=user_ids[i % len(user_ids)],
                title=title,
                status=status,
                duration=duration
            )
            db.add(video)
            print(f"✓ 添加视频: {title}")
        else:
            print(f"- 视频已存在: {title}")

    db.commit()

    print("\n=== 添加测试任务 ===")
    tasks_data = [
        ('novel_generation', 'completed', 100),
        ('novel_generation', 'running', 65),
        ('video_generation', 'completed', 100),
        ('video_generation', 'pending', 0),
        ('video_generation', 'failed', 30),
        ('novel_generation', 'running', 45),
        ('video_generation', 'completed', 100),
    ]

    for i, (task_type, status, progress) in enumerate(tasks_data):
        task = Task(
            user_id=user_ids[i % len(user_ids)],
            task_type=task_type,
            status=status,
            progress=progress
        )
        db.add(task)
        print(f"✓ 添加任务: {task_type} - {status}")

    db.commit()

    print("\n=== 验证数据 ===")
    print(f"用户数: {db.query(User).count()}")
    print(f"小说数: {db.query(Novel).count()}")
    print(f"视频数: {db.query(Video).count()}")
    print(f"任务数: {db.query(Task).count()}")

    print("\n✓ 测试数据添加完成！")

finally:
    db.close()
