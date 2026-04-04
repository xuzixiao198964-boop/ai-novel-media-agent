"""
运行所有测试的脚本
"""
import subprocess
import sys


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行单元测试...")
    print("=" * 60)
    result = subprocess.run([
        "pytest",
        "backend/tests/unit/",
        "-v",
        "--tb=short",
        "-m", "unit"
    ])

    if result.returncode != 0:
        print("\n单元测试失败！")
        return False

    print("\n" + "=" * 60)
    print("运行集成测试...")
    print("=" * 60)
    result = subprocess.run([
        "pytest",
        "backend/tests/integration/",
        "-v",
        "--tb=short",
        "-m", "integration"
    ])

    if result.returncode != 0:
        print("\n集成测试失败！")
        return False

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
