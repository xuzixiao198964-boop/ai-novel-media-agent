# 管理后台手动部署指南

## 1. 准备文件

已生成的文件：
- `E:/work/ai-novel-media-agent/admin/admin-dist.tar.gz` (构建产物压缩包)

## 2. 上传文件到服务器

使用 WinSCP、FileZilla 或其他 SFTP 工具：

**服务器信息：**
- IP: 104.244.90.202
- 用户: root
- 密码: vDyCuc83NxWw
- 端口: 22

**上传步骤：**
1. 连接到服务器
2. 上传 `admin-dist.tar.gz` 到 `/tmp/` 目录

## 3. SSH登录服务器执行命令

使用 PuTTY、MobaXterm 或其他 SSH 工具登录服务器，然后执行以下命令：

```bash
# 创建目录
mkdir -p /var/www/admin

# 解压文件
cd /var/www/admin
tar -xzf /tmp/admin-dist.tar.gz

# 设置权限
chown -R www-data:www-data /var/www/admin
chmod -R 755 /var/www/admin

# 清理临时文件
rm /tmp/admin-dist.tar.gz
```

## 4. 更新 Nginx 配置

编辑 Nginx 配置文件：

```bash
nano /etc/nginx/sites-available/default
```

替换为以下内容：

```nginx
server {
    listen 80;
    server_name _;

    # 官网
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 用户端应用
    location /app {
        alias /var/www/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    # 管理后台
    location /admin {
        alias /var/www/admin;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:9000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:9000/openapi.json;
        proxy_set_header Host $host;
    }
}
```

## 5. 重启 Nginx

```bash
# 测试配置
nginx -t

# 重启服务
systemctl restart nginx
```

## 6. 验证部署

访问以下地址验证：

- **管理后台**: http://104.244.90.202/admin/
- **用户端应用**: http://104.244.90.202/app/
- **产品官网**: http://104.244.90.202/
- **API文档**: http://104.244.90.202/docs

## 7. 测试账号

- 用户名: 15606537209
- 密码: 198964

## 故障排查

如果管理后台无法访问：

```bash
# 检查文件是否存在
ls -la /var/www/admin/

# 检查 Nginx 状态
systemctl status nginx

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log

# 检查文件权限
ls -la /var/www/admin/index.html
```
