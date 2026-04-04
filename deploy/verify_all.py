#!/usr/bin/env python3
import requests

def verify_deployment():
    print("验证部署状态...\n")

    tests = [
        ("官网", "http://104.244.90.202/"),
        ("用户端应用", "http://104.244.90.202/app/"),
        ("管理后台", "http://104.244.90.202/admin/"),
        ("API文档", "http://104.244.90.202/docs"),
        ("后端健康检查", "http://104.244.90.202/api/health"),
    ]

    results = []
    for name, url in tests:
        try:
            resp = requests.get(url, timeout=10)
            status = "OK" if resp.status_code == 200 else f"ERROR {resp.status_code}"
            results.append((name, url, status))
            print(f"[{status}] {name}: {url}")
        except Exception as e:
            results.append((name, url, f"FAIL: {e}"))
            print(f"[FAIL] {name}: {url} - {e}")

    print("\n" + "="*60)
    print("部署验证完成！")
    print("="*60)
    print("\n访问地址：")
    print("- 官网: http://104.244.90.202/")
    print("- 用户端: http://104.244.90.202/app/")
    print("- 管理后台: http://104.244.90.202/admin/")
    print("- API文档: http://104.244.90.202/docs")
    print("\n测试账号: 15606537209 / 198964")

if __name__ == "__main__":
    verify_deployment()
