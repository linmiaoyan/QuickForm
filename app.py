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

# 国际化支持
from core.i18n import translate, get_locale
@app.context_processor
def inject_locale():
    """注入语言环境到模板"""
    return dict(get_locale=get_locale, translate=translate)

# 初始化扩展
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'quickform.login'

bcrypt = Bcrypt(app)

# 导入模型
from core.models import Base, User, Task, Submission, AIConfig

# 数据库配置 - 优先检查MySQL配置，如果配置了MySQL就使用MySQL
MYSQL_HOST = os.getenv('MYSQL_HOST', '')
MYSQL_USER = os.getenv('MYSQL_USER', '')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'quickform')

# 如果环境变量中明确指定了DATABASE_TYPE，使用指定的类型
# 否则，如果MySQL配置完整，优先使用MySQL；否则使用SQLite
if os.getenv('DATABASE_TYPE'):
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
elif MYSQL_HOST and MYSQL_USER and MYSQL_PASSWORD:
    DATABASE_TYPE = 'mysql'
    logger.info("检测到MySQL配置，自动使用MySQL数据库")
else:
    DATABASE_TYPE = 'sqlite'
    logger.info("未检测到MySQL配置，使用SQLite数据库")

# 导入并注册QuickForm Blueprint
from core.blueprint import quickform_bp, init_quickform, SessionLocal
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
    port = int(os.getenv('FLASK_PORT', '80'))
    
    logger.info(f"QuickForm 正在启动...")
    logger.info(f"数据库类型: {DATABASE_TYPE}")
    logger.info(f"调试模式: {debug_mode}")
    logger.info(f"端口: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
