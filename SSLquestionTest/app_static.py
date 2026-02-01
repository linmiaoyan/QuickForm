"""
静态模块测试 - 仅包含不易出错的模块，不涉及网络调用。
包含：Flask、SSL、i18n、静态文件、本地文件读取。
不包含：数据库、AI 服务、邮件、Blueprint 业务逻辑。

若此应用长时间运行稳定，而 app_network 出现无法访问，则问题更可能在网络相关模块。
"""
import os
import ssl
import json
import logging
from flask import Flask

# 确保从 QuickForm 根目录可导入
import sys
_quickform_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _quickform_root not in sys.path:
    sys.path.insert(0, _quickform_root)

from core.i18n import translate, get_locale, get_locale_name

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(_quickform_root, 'static'))
app.secret_key = os.environ.get('SECRET_KEY', 'static_test_secret')


@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale, translate=translate, get_locale_name=get_locale_name)


@app.route('/')
def index():
    return f'app_static OK - 静态模块测试 ({translate("home.welcome")})', 200


@app.route('/ping')
def ping():
    return 'pong', 200


@app.route('/docs')
def docs():
    """本地文件读取测试（不涉及网络）"""
    tutorials_path = os.path.join(app.static_folder, 'tutorials', 'tutorials.json')
    if os.path.exists(tutorials_path):
        try:
            with open(tutorials_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {'status': 'ok', 'tutorials_count': len(data) if isinstance(data, list) else 0}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500
    return {'status': 'ok', 'message': 'tutorials.json not found'}, 200


# 日志过滤器（与主程序一致）
class SecurityScanFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'getMessage'):
            msg = record.getMessage()
            if any(x in msg for x in ['RTSP/1.0', 'Bad request version', 'Bad HTTP/0.9']):
                return False
        return True


werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(SecurityScanFilter())


def _make_ssl_context():
    cert = os.path.join(_quickform_root, 'certs', 'quickform.cn.pem')
    key = os.path.join(_quickform_root, 'certs', 'quickform.cn.key')
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        if hasattr(ssl, 'TLSVersion') and hasattr(ctx, 'minimum_version'):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return ctx
    except Exception as e:
        logger.warning("SSL 证书加载失败: %s", e)
        return (cert, key)


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', '8443'))
    logger.info("app_static 启动: 0.0.0.0:%d (HTTPS) - 仅静态模块", port)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
        ssl_context=_make_ssl_context(),
    )
