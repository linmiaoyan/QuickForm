# QuickForm 看门狗说明

## 作用

- **定期访问首页**做健康检查（默认每 5 分钟一次）。
- **若无法访问**：先等 60 秒再试一次；仍失败则**自动重启主进程**，并**累计重启次数**。
- 重启后应用仍使用同一 `SECRET_KEY`，**Flask 的 session cookie 不变**，已登录用户**无需重新登录**。

## 使用方式

**推荐**：用看门狗启动，代替直接运行 `app.py`。

- 双击运行：`run_with_watchdog.bat`
- 或命令行（在项目根目录）：
  ```bash
  python scripts\watchdog.py
  ```

主程序仍按原来的方式在 443 端口、HTTPS 运行，只是由看门狗子进程启动和监控。

## 重启次数统计

- 统计文件：项目根目录下的 **`watchdog_refresh.json`**。
- 内容示例：
  ```json
  {
    "refresh_count": 2,
    "last_refresh_at": "2026-02-04T12:00:00",
    "last_check_ok_at": "2026-02-04T11:55:00"
  }
  ```
- `refresh_count`：累计自动重启次数。  
- `last_refresh_at`：最近一次重启时间。  
- `last_check_ok_at`：最近一次健康检查成功时间。

## 可选配置（环境变量）

| 变量 | 含义 | 默认值 |
|------|------|--------|
| `WATCHDOG_URL` | 健康检查地址 | `https://127.0.0.1:443/` |
| `WATCHDOG_INTERVAL` | 检查间隔（秒） | `300`（5 分钟） |
| `WATCHDOG_TIMEOUT` | 单次请求超时（秒） | `15` |
| `WATCHDOG_RETRY_DELAY` | 首次失败后隔多少秒再试一次 | `60` |

例如希望改为每 10 分钟检查一次：

```bash
set WATCHDOG_INTERVAL=600
python scripts\watchdog.py
```

## 为何重启后不用重新登录？

Flask 的登录状态存在**签名 Cookie**里，签名用的是 `app.secret_key`。看门狗只是重启 Python 进程，不修改配置，`SECRET_KEY` 不变，所以浏览器里已有的 session cookie 仍然有效，用户会保持登录状态。
