#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速测试脚本 - 验证MVP功能"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("Testing imports...")
    try:
        from app.config import settings
        print("[OK] Config loaded")

        from app.database import Base, engine, get_db, init_db
        print("[OK] Database module loaded")

        from app.models import User, Task, Novel
        print("[OK] Models loaded")

        from app.api.auth import router as auth_router
        print("[OK] Auth API loaded")

        from app.api.tasks import router as tasks_router
        print("[OK] Tasks API loaded")

        from app.agents.trend import TrendAgent
        print("[OK] TrendAgent loaded")

        from app.agents.writer import WriterAgent
        print("[OK] WriterAgent loaded")

        from app.main import app
        print("[OK] FastAPI app loaded")

        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库初始化"""
    print("\nTesting database...")
    try:
        from app.database import init_db
        init_db()
        print("[OK] Database initialized")

        # 检查数据库文件
        if os.path.exists("data/app.db"):
            print("[OK] Database file created")
        else:
            print("[FAIL] Database file not found")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agents():
    """测试Agent功能"""
    print("\nTesting agents...")
    try:
        import asyncio
        from app.agents.trend import TrendAgent
        from app.agents.writer import WriterAgent

        # 测试TrendAgent
        trend_agent = TrendAgent(task_id="test_task_001")
        result = asyncio.run(trend_agent.execute())

        if result.success:
            print("[OK] TrendAgent works")
        else:
            print("[FAIL] TrendAgent failed")
            return False

        # 测试WriterAgent
        writer_agent = WriterAgent(task_id="test_task_002", config={
            "chapter_num": 1,
            "planning": {
                "chapter_outlines": [
                    {
                        "title": "第一章 测试章节",
                        "summary": "这是一个测试章节的大纲"
                    }
                ]
            }
        })
        result = asyncio.run(writer_agent.execute())

        if result.success:
            print("[OK] WriterAgent works")
        else:
            print("[FAIL] WriterAgent failed")
            return False

        return True
    except Exception as e:
        print(f"[FAIL] Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("AI Novel Media Agent - MVP Test")
    print("=" * 50)

    results = []

    # 测试导入
    results.append(("Imports", test_imports()))

    # 测试数据库
    results.append(("Database", test_database()))

    # 测试Agents
    results.append(("Agents", test_agents()))

    # 总结
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("\n[OK] All tests passed! Ready to start server.")
        print("\nRun: python -m uvicorn app.main:app --reload")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
