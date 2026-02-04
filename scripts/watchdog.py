# -*- coding: utf-8 -*-
"""
QuickForm 看门狗：定期访问首页做健康检查，失败时自动重启主进程并统计重启次数。
重启后使用相同 SECRET_KEY，Flask session cookie 仍有效，用户无需重新登录。

用法（在 QuickForm 项目根目录）：
    python scripts/watchdog.py
或先 cd 到项目根再：
    python scripts\watchdog.py

环境变量（可选）：
    WATCHDOG_URL           健康检查地址，默认 https://127.0.0.1:443/
    WATCHDOG_INTERVAL      检查间隔（秒），默认 300（5 分钟）
    WATCHDOG_TIMEOUT       单次请求超时（秒），默认 15
    WATCHDOG_RETRY_DELAY   首次失败后隔多少秒再试一次再决定重启，默认 60
"""
import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# 优先用 requests；若无则用 urllib + ssl（HTTPS 不校验自签名证书）
import urllib.request
import ssl as ssl_mod

_USE_REQUESTS = False
try:
    import requests
    _USE_REQUESTS = True
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 项目根目录 = 本脚本所在目录的上一级
ROOT_DIR = Path(__file__).resolve().parent.parent
REFRESH_FILE = ROOT_DIR / "watchdog_refresh.json"

# 配置（可被环境变量覆盖）
def _env_int(name, default):
    v = os.getenv(name)
    return int(v) if v and v.isdigit() else default

CHECK_URL = os.getenv("WATCHDOG_URL", "https://127.0.0.1:443/").strip()
CHECK_INTERVAL = _env_int("WATCHDOG_INTERVAL", 300)
CHECK_TIMEOUT = _env_int("WATCHDOG_TIMEOUT", 15)
RETRY_DELAY = _env_int("WATCHDOG_RETRY_DELAY", 60)


def load_refresh_data():
    data = {"refresh_count": 0, "last_refresh_at": None, "last_check_ok_at": None}
    if REFRESH_FILE.exists():
        try:
            with open(REFRESH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning("读取刷新统计失败: %s", e)
    return data


def save_refresh_data(data):
    try:
        with open(REFRESH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("写入刷新统计失败: %s", e)


def health_check():
    """访问首页，成功返回 True，失败返回 False。"""
    try:
        if _USE_REQUESTS:
            r = requests.get(
                CHECK_URL,
                timeout=CHECK_TIMEOUT,
                verify=False
            )
            ok = r.status_code == 200
        else:
            ctx = ssl_mod.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl_mod.CERT_NONE
            req = urllib.request.Request(CHECK_URL, method="GET")
            with urllib.request.urlopen(req, timeout=CHECK_TIMEOUT, context=ctx) as resp:
                ok = resp.status == 200
        return ok
    except Exception as e:
        logger.debug("健康检查请求异常: %s", e)
        return False


def main():
    os.chdir(ROOT_DIR)
    app_script = ROOT_DIR / "app.py"
    if not app_script.exists():
        logger.error("未找到 app.py，请确保在 QuickForm 项目根目录运行本脚本。")
        sys.exit(1)

    data = load_refresh_data()
    logger.info(
        "看门狗启动。检查地址=%s，间隔=%ds，超时=%ds。历史重启次数=%d",
        CHECK_URL, CHECK_INTERVAL, CHECK_TIMEOUT, data.get("refresh_count", 0)
    )

    # 若使用 requests 且是 HTTPS，屏蔽 InsecureRequestWarning
    if _USE_REQUESTS and CHECK_URL.lower().startswith("https://"):
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass

    while True:
        proc = subprocess.Popen(
            [sys.executable, str(app_script)],
            cwd=str(ROOT_DIR),
            env=os.environ.copy(),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        logger.info("主进程已启动 PID=%s，等待 %ds 后开始健康检查…", proc.pid, min(30, CHECK_INTERVAL))
        time.sleep(min(30, CHECK_INTERVAL))

        while True:
            time.sleep(CHECK_INTERVAL)
            if proc.poll() is not None:
                logger.warning("主进程已退出 code=%s，将重新启动。", proc.returncode)
                break

            if health_check():
                data["last_check_ok_at"] = datetime.now().isoformat()
                save_refresh_data(data)
                logger.debug("健康检查通过。")
                continue

            logger.warning("健康检查失败，%ds 后重试一次…", RETRY_DELAY)
            time.sleep(RETRY_DELAY)
            if proc.poll() is not None:
                logger.warning("主进程已退出，将重新启动。")
                break
            if health_check():
                data["last_check_ok_at"] = datetime.now().isoformat()
                save_refresh_data(data)
                logger.info("重试检查通过，继续监控。")
                continue

            logger.warning("重试仍失败，执行重启（保留 session，用户无需重新登录）。")
            data["refresh_count"] = data.get("refresh_count", 0) + 1
            data["last_refresh_at"] = datetime.now().isoformat()
            save_refresh_data(data)
            try:
                proc.terminate()
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
            except Exception as e:
                logger.error("结束主进程异常: %s", e)
            logger.info("已重启主进程，当前累计重启次数: %d", data["refresh_count"])
            break


if __name__ == "__main__":
    main()
