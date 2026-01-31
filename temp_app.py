"""
最小化测试应用 - 仅模拟主程序启动，不引用 QuickForm 业务逻辑。
用于排查：若此应用同样在约 6 小时后无响应，则问题更可能在 Flask/Werkzeug/SSL 层；
若此应用稳定，则问题更可能在 QuickForm 业务代码。

用法：在项目根目录执行 python temp_app.py
注意：443 端口需先停止主程序；或设置 FLASK_PORT=8443 与主程序并存测试。
"""
import os
import ssl
import logging
from flask import Flask

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    return 'temp_app OK - 最小化测试运行中', 200


def _make_ssl_context():
    """与主程序相同的 SSL 配置"""
    cert = r"certs\quickform.cn.pem"
    key = r"certs\quickform.cn.key"
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        if hasattr(ssl, 'TLSVersion') and hasattr(ctx, 'minimum_version'):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return ctx
    except Exception as e:
        logger.warning("SSL 证书加载失败: %s，将使用 (cert, key) 元组", e)
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
