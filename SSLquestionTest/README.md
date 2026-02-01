# SSL/网络问题排查 - 拆分测试

用于排查「服务运行数小时后无法被外部访问」的问题。  
temp_app 已验证可长时间运行，现通过拆分进一步缩小范围。

## 三个测试应用

| 应用 | 包含模块 | 默认端口 | 说明 |
|------|----------|----------|------|
| **temp_app.py** | 仅 Flask + SSL | 443 | 最小化，已验证可稳定运行 12+ 小时 |
| **app_static.py** | Flask、SSL、i18n、静态文件、本地 JSON 读取 | 8443 | 无数据库、无 AI、无邮件 |
| **app_network.py** | 完整 QuickForm（数据库、AI、邮件、Blueprint） | 443 | 包含所有可能产生网络类错误的模块 |

## 使用方法

在 **QuickForm 项目根目录** 执行（或在 SSLquestionTest 内执行，脚本会切换工作目录）：

```cmd
cd D:\OneDrive\09教育技术处\QuickForm

REM 测试静态模块（与 temp_app 并存可设不同端口）
set FLASK_PORT=8443
python SSLquestionTest\app_static.py

REM 测试完整应用（需先停止 app_static，443 端口唯一）
set FLASK_PORT=443
python SSLquestionTest\app_network.py
```

## 排查结论

- **temp_app** 稳定 + **app_static** 稳定 + **app_network** 异常 → 问题在数据库/AI/邮件等网络模块
- **temp_app** 稳定 + **app_static** 异常 → 问题在 i18n 或静态文件服务
- **temp_app** 异常 → 问题在 Flask/Werkzeug/SSL 层或系统环境
