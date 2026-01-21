# QuickForm 架构重构说明

## 📋 重构概述

本次重构将QuickForm从**蓝图式架构**改为**独立应用架构**，主要变更如下：

### 变更内容

1. **✅ 架构调整**
   - 将 `QuickForm/` 子目录的内容提升到主目录
   - 删除嵌套的目录结构
   - 创建新的独立 `app.py` 入口文件

2. **✅ 新增功能**
   - 管理员删除用户功能
   - 用户数据导出(Excel格式)
   - 用户数据统计可视化页面
   - 级联删除(删除用户时自动删除相关数据)

3. **🗑️ 移除内容**
   - 删除 `main.py`(不再需要)
   - 删除 `ChatServer/` 目录(独立应用不需要)
   - 删除 `Votesite/` 目录(独立应用不需要)

## 🚀 执行重构

### 方法1: 使用自动化脚本(推荐)

**⚠️ 重要提示：执行前请确保已备份或提交到Git！**

```powershell
# 在QuickForm主目录执行
.\restructure.ps1
```

### 方法2: 手动重构

如果脚本执行失败，可以手动执行以下步骤：

#### 步骤1: 移动文件

```powershell
# 移动Python文件
Copy-Item .\QuickForm\*.py -Destination . -Force

# 移动templates目录
Remove-Item .\templates -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item .\QuickForm\templates -Destination .\templates -Recurse -Force

# 移动试题范例
Copy-Item ".\QuickForm\试题范例" -Destination ".\试题范例" -Recurse -Force

# 移动README
Copy-Item .\QuickForm\README*.md -Destination . -Force
```

#### 步骤2: 创建新的app.py

创建 `app.py` 文件，内容见 `restructure.ps1` 中的模板。

#### 步骤3: 删除旧文件

```powershell
# 删除不需要的目录
Remove-Item .\main.py -Force
Remove-Item .\ChatServer -Recurse -Force
Remove-Item .\Votesite -Recurse -Force
Remove-Item .\QuickForm -Recurse -Force
```

## 📝 重构后的目录结构

```
QuickForm/
├── app.py                  # 新的应用入口
├── blueprint.py            # Blueprint定义
├── models.py              # 数据模型
├── ai_service.py          # AI服务
├── file_service.py        # 文件服务
├── report_service.py      # 报告服务
├── utils.py               # 工具函数
├── requirements.txt       # 依赖列表
├── .env                   # 环境变量(自行创建)
├── .env.example           # 环境变量示例
├── .gitignore            # Git忽略文件
├── 1push.bat             # Git推送脚本
├── 2pull_normal.bat      # Git拉取脚本
├── 3pull_force.bat       # Git强制拉取脚本
├── templates/            # 模板文件夹
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── admin_user_statistics.html  # 新增：用户统计页面
│   └── ...
├── static/               # 静态资源
│   ├── css/
│   ├── js/
│   └── ...
├── uploads/             # 上传文件目录
│   ├── reports/
│   └── certifications/
└── 试题范例/            # 示例文件

已删除:
- main.py               # 蓝图式架构的主入口
- QuickForm/            # 嵌套目录
- ChatServer/           # 聊天服务器模块
- Votesite/            # 投票系统模块
```

## 🔧 配置说明

### 环境变量配置

创建 `.env` 文件：

```ini
# Flask配置
SECRET_KEY=your_secret_key_here_change_this
FLASK_DEBUG=False
FLASK_PORT=5001

# 数据库配置
DATABASE_TYPE=sqlite  # 或 mysql

# MySQL配置(如果使用MySQL)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=quickform
```

### 数据库说明

- **SQLite**: 默认使用，无需额外配置，数据存储在 `quickform.db` 文件中
- **MySQL**: 需要设置环境变量，参考上面的配置

## 🎯 启动应用

重构后的启动方式：

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 访问应用
# http://localhost:5001/quickform
```

## 🆕 新增功能使用说明

### 1. 删除用户

管理员面板 → 用户管理 → 选择用户 → 点击"删除用户"按钮

**功能说明：**
- 仅管理员可以删除用户
- 不能删除自己和其他管理员
- 删除用户时会级联删除：
  - 用户的所有任务
  - 任务的所有提交数据
  - AI配置
  - 认证申请
- 操作不可恢复，请谨慎使用

### 2. 用户数据导出

管理员面板 → 用户管理 → 点击"导出Excel"按钮

**导出内容：**
- 用户基本信息(ID、用户名、邮箱、学校、手机)
- 角色和认证状态
- 任务数量和数据提交数
- 注册时间

### 3. 用户数据统计

管理员面板 → 用户管理 → 点击"数据统计"按钮

**统计内容：**
- 用户概览(总数、管理员数、认证用户数)
- 用户学校分布(饼图)
- 最近30天注册趋势(折线图)
- 用户任务排行榜(柱状图，Top 20)

## ⚠️ 注意事项

1. **Git仓库**
   - 重构后需要初始化新的Git仓库或提交更改
   - 原有的仓库地址需要更新为 QuickForm

2. **数据保留**
   - `quickform.db` 数据库文件会保留
   - `uploads/` 目录会保留
   - 用户数据不会丢失

3. **启动方式变更**
   - 旧: `python main.py`
   - 新: `python app.py`
   - 访问路径变更: `http://localhost:5001/quickform`

4. **依赖检查**
   - 重构后建议重新安装依赖
   - 确保 `pandas`, `openpyxl` 等库已安装

## 🐛 故障排除

### 问题1: 导入错误

```
ModuleNotFoundError: No module named 'models'
```

**解决方案：** 确保所有Python文件都在主目录，检查文件是否正确移动。

### 问题2: 数据库连接失败

```
Database connection error
```

**解决方案：** 
- 检查 `.env` 文件配置
- 如果使用MySQL，确认数据库已创建且权限正确
- 使用SQLite可以避免此问题

### 问题3: 模板找不到

```
TemplateNotFound: admin_user_statistics.html
```

**解决方案：** 确保 `templates/` 目录完整移动到主目录。

## 📞 技术支持

如有问题，请联系：
- 邮箱: wzlinmiaoyan@163.com
- 管理员账号: wzkjgz / wzkjgz123!

## 📄 更新日志

### v2.0.0 (2026-01-13)

**架构重构**
- 从蓝图式架构改为独立应用架构
- 简化目录结构，提升代码可维护性

**新增功能**
- 管理员删除用户功能(含级联删除)
- 用户数据导出为Excel
- 用户数据统计可视化(ECharts图表)
- 用户学校分布、注册趋势、任务排行榜

**优化改进**
- 改进数据模型，添加级联删除支持
- 优化管理员面板界面
- 增强错误处理和日志记录

**移除内容**
- 移除ChatServer模块(已独立)
- 移除Votesite模块(已独立)
- 移除main.py主入口文件
