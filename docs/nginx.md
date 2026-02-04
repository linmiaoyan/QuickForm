# Nginx 反向代理 QuickForm

Flask 已改为**仅 HTTP、监听本机**（默认 `127.0.0.1:5000`），SSL 与对外端口由 Nginx 负责。

## 1. 启动 Flask（内网服务）

在项目根目录：

```bash
python app.py
```

或设置环境变量：

- `FLASK_HOST`：监听地址，默认 `127.0.0.1`
- `FLASK_PORT`：监听端口，默认 `5000`

## 2. Nginx 配置示例

将下面内容根据实际情况改好后，放入 Nginx 的 `server` 配置中（例如 `conf.d/quickform.conf` 或主配置里的 `http { ... }` 内）。

### 仅 HTTP（80 端口）

```nginx
server {
    listen 80;
    server_name your-domain.com;   # 改成你的域名或 IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### HTTPS（443）+ HTTP 跳转（推荐）

```nginx
# HTTP 跳转到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;

    # SSL 证书（路径按你实际放置位置改）
    ssl_certificate     /path/to/your/cert.pem;      # 或 fullchain.pem
    ssl_certificate_key /path/to/your/privkey.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

说明：

- `proxy_pass http://127.0.0.1:5000` 对应 Flask 默认端口，若你改了 `FLASK_PORT`，这里要一起改。
- `X-Forwarded-Proto` 必须为 `https`，Flask 里已用 ProxyFix，会据此生成正确的 https 链接和 `request.is_secure`。

## 3. 应用配置并重载 Nginx

- Windows（以管理员运行）：  
  `nginx -s reload`  
  或先测试配置：`nginx -t` 再 `nginx -s reload`。

- Linux：  
  `sudo nginx -t && sudo systemctl reload nginx`  
  或 `sudo nginx -s reload`。

## 4. 流程小结

1. 先启动 Flask：`python app.py`（监听 127.0.0.1:5000）。
2. 再确保 Nginx 已加载上述配置并 reload。
3. 用户访问 `http://your-domain.com` 或 `https://your-domain.com`，由 Nginx 转发到本机 5000，Flask 无需再配 SSL。
