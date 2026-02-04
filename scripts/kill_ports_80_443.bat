@echo off
chcp 65001 >nul
echo 正在查找并关闭占用 80 和 443 端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":80 "') do (echo 关闭端口 80 的 PID: %%a & taskkill /PID %%a /F 2>nul)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":443 "') do (echo 关闭端口 443 的 PID: %%a & taskkill /PID %%a /F 2>nul)
echo 完成.
pause
