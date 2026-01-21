@echo off
chcp 65001 >nul
title 导入QuickForm数据库
color 0E

echo ========================================
echo   QuickForm 数据库导入工具
echo ========================================
echo.

set /p mysql_password=请输入MySQL root密码: 

echo.
echo 正在导入，请稍候...
echo.

cd /d "C:\Program Files\MySQL\MySQL Server 9.5\bin"

:: 删除旧数据库
mysql.exe -u root -p%mysql_password% -e "DROP DATABASE IF EXISTS quickform;" 2>nul

:: 创建新数据库
mysql.exe -u root -p%mysql_password% -e "CREATE DATABASE quickform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul

:: 修复SQL文件（删除GTID）
findstr /V /C:"SET @@GLOBAL.GTID_PURGED" "D:\Download\quickform_backup.sql" > "D:\Download\quickform_backup_fixed.sql"

:: 导入数据
mysql.exe -u root -p%mysql_password% quickform < "D:\Download\quickform_backup_fixed.sql"

if %errorlevel% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ 导入成功！
    echo ========================================
    echo.
    echo 验证数据...
    mysql.exe -u root -p%mysql_password% -e "USE quickform; SHOW TABLES;"
    echo.
    echo 下一步:
    echo   1. 编辑 .env 文件，设置 DATABASE_TYPE=mysql
    echo   2. 双击"启动应用.bat"启动应用
    echo   3. 访问 http://localhost:5001/quickform
    echo.
) else (
    echo.
    echo ✗ 导入失败，请检查错误信息
    echo.
)

pause
