@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 使用看门狗启动 QuickForm：将定期检查首页，无响应时自动重启并统计次数，重启后用户无需重新登录。
echo.
python scripts\watchdog.py
pause
