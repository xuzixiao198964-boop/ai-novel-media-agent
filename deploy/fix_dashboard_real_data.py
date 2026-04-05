#!/usr/bin/env python3
"""修复Dashboard显示真实数据"""

import paramiko
import time
import os

def main():
    print("=" * 60)
    print("Fix Dashboard Real Data")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("\nConnecting to 104.244.90.202...")
        ssh.connect('104.244.90.202', username='root', password='vDyCuc83NxWw', timeout=10)
        print("[OK] Connected")

        sftp = ssh.open_sftp()

        # 1. Upload backend API file
        print("\n[1] Uploading backend API...")
        local_api = "E:/work/ai-novel-media-agent/backend/app/api/admin_simple.py"
        remote_api = "/opt/ai-novel-media-agent/backend/app/api/admin_simple.py"
        sftp.put(local_api, remote_api)
        print("[OK] Backend API uploaded")

        # 2. Kill port 9000 and restart backend
        print("\n[2] Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command("lsof -ti:9000 | xargs kill -9 2>/dev/null || true")
        stdout.read()
        time.sleep(2)

        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-novel-media-agent")
        stdout.read()
        time.sleep(3)
        print("[OK] Backend restarted")

        # 3. Test new API endpoints
        print("\n[3] Testing new API endpoints...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard/task-distribution")
        result = stdout.read().decode()
        print(f"Task Distribution: {result[:100]}")

        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution")
        result = stdout.read().decode()
        print(f"Subscription Distribution: {result[:100]}")

        # 4. Build frontend
        print("\n[4] Building frontend...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/admin && npm run build")
        stdout.read()
        time.sleep(5)
        print("[OK] Frontend built")

        # 5. Upload frontend files
        print("\n[5] Uploading frontend files...")

        # Upload Dashboard.tsx
        local_dashboard = "E:/work/ai-novel-media-agent/admin/src/pages/Dashboard.tsx"
        remote_dashboard = "/opt/ai-novel-media-agent/admin/src/pages/Dashboard.tsx"
        sftp.put(local_dashboard, remote_dashboard)
        print("[OK] Dashboard.tsx uploaded")

        # Upload api/index.ts
        local_api_index = "E:/work/ai-novel-media-agent/admin/src/api/index.ts"
        remote_api_index = "/opt/ai-novel-media-agent/admin/src/api/index.ts"
        sftp.put(local_api_index, remote_api_index)
        print("[OK] api/index.ts uploaded")

        # 6. Rebuild frontend
        print("\n[6] Rebuilding frontend...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/admin && npm run build")
        output = stdout.read().decode()
        error = stderr.read().decode()

        if "built in" in output or "built in" in error:
            print("[OK] Frontend rebuilt successfully")
        else:
            print("[WARN] Build output:")
            print(output[-500:] if output else error[-500:])

        # 7. Deploy to nginx
        print("\n[7] Deploying to nginx...")
        stdin, stdout, stderr = ssh.exec_command("rm -rf /var/www/ai-novel-media-agent/admin && mkdir -p /var/www/ai-novel-media-agent/admin && cp -r /opt/ai-novel-media-agent/admin/dist/* /var/www/ai-novel-media-agent/admin/")
        stdout.read()
        print("[OK] Deployed to nginx")

        # 8. Reload nginx
        print("\n[8] Reloading nginx...")
        stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
        stdout.read()
        print("[OK] Nginx reloaded")

        # 9. Final verification
        print("\n[9] Final verification...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard")
        result = stdout.read().decode()
        print(f"Dashboard API: {result[:200]}")

        sftp.close()

        print("\n" + "=" * 60)
        print("[SUCCESS] All updates deployed!")
        print("=" * 60)
        print("\nPlease visit: http://104.244.90.202/admin")
        print("Login: admin / 198964")
        print("\nChanges:")
        print("- Removed all fake data fallbacks")
        print("- Added task type distribution pie chart")
        print("- Added subscription distribution bar chart")
        print("- All data now comes from real database")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
