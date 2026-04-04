#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试完整用户流程"""
import requests
import time
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://104.244.90.202"
API_URL = f"{BASE_URL}/api"

class TestFlow:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.task_id = None

    def log(self, message, status="INFO"):
        symbols = {
            "INFO": "[*]",
            "SUCCESS": "[+]",
            "ERROR": "[-]",
            "TEST": "[TEST]"
        }
        print(f"{symbols.get(status, '[*]')} {message}")

    def test_1_login(self):
        """测试1: 用户登录"""
        self.log("Testing user login...", "TEST")

        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={
                    "username": "15606537209",
                    "password": "198964"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log(f"Login successful! Token: {self.token[:20]}...", "SUCCESS")
                return True
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Login error: {e}", "ERROR")
            return False

    def test_2_get_user_info(self):
        """测试2: 获取用户信息"""
        self.log("Testing get user info...", "TEST")

        try:
            response = requests.get(
                f"{API_URL}/auth/me",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("user_id")
                self.log(f"User info: {data.get('username')} (ID: {self.user_id})", "SUCCESS")
                return True
            else:
                self.log(f"Get user info failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Get user info error: {e}", "ERROR")
            return False

    def test_3_get_tasks(self):
        """测试3: 获取任务列表"""
        self.log("Testing get tasks list...", "TEST")

        try:
            response = requests.get(
                f"{API_URL}/tasks",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"Tasks count: {len(data)}", "SUCCESS")
                if len(data) > 0:
                    self.log(f"First task: {data[0]}", "INFO")
                return True
            else:
                self.log(f"Get tasks failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Get tasks error: {e}", "ERROR")
            return False

    def test_4_create_task(self):
        """测试4: 创建小说任务"""
        self.log("Testing create novel task...", "TEST")

        try:
            response = requests.post(
                f"{API_URL}/tasks",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "task_type": "novel_only",
                    "input_data": {
                        "novel_config": {
                            "length_type": "short",
                            "genre": "fantasy",
                            "sub_genres": ["xuanhuan", "xianxia"]
                        }
                    }
                },
                timeout=10
            )

            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                self.task_id = data.get("task_id")
                self.log(f"Task created! ID: {self.task_id}", "SUCCESS")
                return True
            else:
                self.log(f"Create task failed: {response.status_code} - {response.text}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Create task error: {e}", "ERROR")
            return False

    def test_5_get_task_detail(self):
        """测试5: 获取任务详情"""
        if not self.task_id:
            self.log("No task_id, skipping...", "INFO")
            return True

        self.log("Testing get task detail...", "TEST")

        try:
            response = requests.get(
                f"{API_URL}/tasks/{self.task_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"Task status: {data.get('status')}, Progress: {data.get('progress')}%", "SUCCESS")
                return True
            else:
                self.log(f"Get task detail failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Get task detail error: {e}", "ERROR")
            return False

    def test_6_get_novels(self):
        """测试6: 获取小说列表"""
        self.log("Testing get novels list...", "TEST")

        try:
            response = requests.get(
                f"{API_URL}/novels",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"Novels count: {len(data)}", "SUCCESS")
                return True
            else:
                self.log(f"Get novels failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Get novels error: {e}", "ERROR")
            return False

    def test_7_get_videos(self):
        """测试7: 获取视频列表"""
        self.log("Testing get videos list...", "TEST")

        try:
            response = requests.get(
                f"{API_URL}/videos",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"Videos count: {len(data)}", "SUCCESS")
                return True
            else:
                self.log(f"Get videos failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Get videos error: {e}", "ERROR")
            return False

    def test_8_frontend_pages(self):
        """测试8: 前端页面访问"""
        self.log("Testing frontend pages...", "TEST")

        pages = [
            ("Official Site", f"{BASE_URL}/"),
            ("User App", f"{BASE_URL}/app/"),
            ("API Docs", f"{BASE_URL}/docs"),
        ]

        success = 0
        for name, url in pages:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"{name}: OK", "SUCCESS")
                    success += 1
                else:
                    self.log(f"{name}: Failed ({response.status_code})", "ERROR")
            except Exception as e:
                self.log(f"{name}: Error ({e})", "ERROR")

        return success == len(pages)

    def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 60, "INFO")
        self.log("Starting Full Flow Test", "INFO")
        self.log("=" * 60, "INFO")

        tests = [
            self.test_1_login,
            self.test_2_get_user_info,
            self.test_3_get_tasks,
            self.test_4_create_task,
            self.test_5_get_task_detail,
            self.test_6_get_novels,
            self.test_7_get_videos,
            self.test_8_frontend_pages,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"Test exception: {e}", "ERROR")
                failed += 1

            time.sleep(0.5)

        self.log("=" * 60, "INFO")
        self.log(f"Test Results: {passed} passed, {failed} failed", "INFO")
        self.log("=" * 60, "INFO")

        return failed == 0

if __name__ == "__main__":
    tester = TestFlow()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
