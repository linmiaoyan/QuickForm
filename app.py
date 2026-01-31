"""QuickForm 独立应用入口"""
import os
import ssl
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
app.config['PREFERRED_URL_SCHEME'] = 'https'  # 统一生成 https 链接

# 邮件发送配置（用于邮箱验证码）
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.163.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # 你的163邮箱，例如 xxx@163.com
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # 163邮箱的SMTP授权码（不要写死在代码里）
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# 国际化支持
from core.i18n import translate, get_locale, get_locale_name
@app.context_processor
def inject_locale():
    """注入语言环境到模板"""
    return dict(get_locale=get_locale, translate=translate, get_locale_name=get_locale_name)

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
    logger.info("检测到 MySQL 配置，将使用 MySQL 数据库")
else:
    DATABASE_TYPE = 'sqlite'
    logger.info("未检测到 MySQL 配置，将使用 SQLite 数据库")

# 导入并注册QuickForm Blueprint
from core.blueprint import quickform_bp, init_quickform, SessionLocal
init_quickform(app, login_manager, database_type=DATABASE_TYPE)

# 注册Blueprint
app.register_blueprint(quickform_bp)

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

def _make_ssl_context():
    """直接运行 app 时使用的 SSL 上下文。用 gunicorn/反向代理时不需要。"""
    cert = r"certs\quickform.cn.pem"
    key = r"certs\quickform.cn.key"
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        if hasattr(ssl, 'TLSVersion') and hasattr(ctx, 'minimum_version'):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return ctx
    except Exception:
        return (cert, key)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '443'))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        use_reloader=False,
        threaded=True,  # 多线程：单请求卡住不会拖死整站，无需额外配 Waitress
        ssl_context=_make_ssl_context(),
    )