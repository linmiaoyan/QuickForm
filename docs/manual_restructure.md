# QuickForm 手动重构步骤

如果PowerShell脚本无法运行,请按以下步骤手动操作:

## 步骤1: 复制Python文件

```powershell
# 在QuickForm目录执行
Copy-Item .\QuickForm\ai_service.py -Destination .
Copy-Item .\QuickForm\file_service.py -Destination .
Copy-Item .\QuickForm\models.py -Destination .
Copy-Item .\QuickForm\report_service.py -Destination .
Copy-Item .\QuickForm\utils.py -Destination .
Copy-Item .\QuickForm\blueprint.py -Destination .
Copy-Item .\QuickForm\check_submission_count.py -Destination .
Copy-Item .\QuickForm\clear_mysql_data.py -Destination .
Copy-Item .\QuickForm\migrate_to_mysql.py -Destination .
Copy-Item .\QuickForm\README.md -Destination .
Copy-Item .\QuickForm\README_MYSQL.md -Destination .
```

## 步骤2: 复制目录

```powershell
# 删除旧的templates(如果存在)
Remove-Item .\templates -Recurse -Force -ErrorAction SilentlyContinue

# 复制新的templates
Copy-Item .\QuickForm\templates -Destination .\templates -Recurse

# 复制试题范例
Copy-Item ".\QuickForm\试题范例" -Destination ".\试题范例" -Recurse -Force
```

## 步骤3: 创建app.py

在QuickForm主目录创建文件 `app.py`,内容如下:

```python
"""QuickForm 独立应用入口"""
import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 初始化扩展
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'quickform.login'

bcrypt = Bcrypt(app)

# 导入模型
from models import Base, User, Task, Submission, AIConfig

# 数据库配置
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')

# 导入并注册QuickForm Blueprint
from blueprint import quickform_bp, init_quickform, SessionLocal
init_quickform(app, login_manager, database_type=DATABASE_TYPE)

# 注册Blueprint
app.register_blueprint(quickform_bp, url_prefix='/quickform')

# User loader
@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.get(User, int(user_id))
    finally:
        db.close()

# 首页重定向
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('quickform.dashboard'))
    return redirect(url_for('quickform.index'))

# 配置日志过滤器
class SecurityScanFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'getMessage'):
            msg = record.getMessage()
            if any(x in msg for x in ['RTSP/1.0', 'Bad request version', 'Bad HTTP/0.9']):
                return False
        return True

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(SecurityScanFilter())

# 错误处理
@app.errorhandler(400)
def bad_request(error):
    return 'Bad Request', 400

@app.errorhandler(404)
def not_found(error):
    return 'Not Found', 404

@app.errorhandler(413)
def request_entity_too_large(error):
    from flask import flash, request
    app.logger.warning(f"413错误 - 请求实体过大")
    flash('文件大小超过服务器限制（最大16MB）', 'danger')
    return redirect(url_for('quickform.dashboard'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', '5001'))
    
    logger.info(f"QuickForm 正在启动...")
    logger.info(f"数据库类型: {DATABASE_TYPE}")
    logger.info(f"调试模式: {debug_mode}")
    logger.info(f"端口: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

## 步骤4: 清理不需要的文件

```powershell
# 删除main.py
Remove-Item .\main.py -Force -ErrorAction SilentlyContinue

# 删除ChatServer和Votesite(如果存在)
Remove-Item .\ChatServer -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\Votesite -Recurse -Force -ErrorAction SilentlyContinue

# 最后删除QuickForm子目录
Remove-Item .\QuickForm -Recurse -Force
```

## 步骤5: 创建.env文件

如果还没有.env文件,创建它:

```ini
# Flask配置
SECRET_KEY=your_secret_key_here_change_this
FLASK_DEBUG=False
FLASK_PORT=5001

# 数据库配置
DATABASE_TYPE=sqlite

# MySQL配置(如果使用)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=quickform
```

## 步骤6: 启动应用

```bash
python app.py
```

访问: http://localhost:5001/quickform

---

## 完成!

现在你的QuickForm已经是独立应用架构了!
