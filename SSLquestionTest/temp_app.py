"""
最小化测试应用 - 仅 Flask + SSL，不引用任何 QuickForm 模块。
（与项目根目录 temp_app.py 逻辑相同，便于在 SSLquestionTest 内统一管理）

若此应用长时间稳定、app_static 也稳定、app_network 异常，则问题在数据库/AI/邮件等模块。
"""
import os
import ssl
import logging
import sys

# 切换到 QuickForm 根目录（证书路径相对根目录）
_quickform_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_quickform_root)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'temp_app OK - 最小化测试运行中', 200


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
    port = int(os.environ.get('FLASK_PORT', '443'))
    logger.info("temp_app 启动: 0.0.0.0:%d (HTTPS)", port)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
        ssl_context=_make_ssl_context(),
    )
