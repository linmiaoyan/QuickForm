"""
网络模块测试 - 完整 QuickForm 应用，包含数据库、AI、邮件等可能产生网络类错误的模块。
导入并运行主程序 app.py。

若此应用出现长时间运行后无法访问，而 app_static 稳定，则问题更可能在网络相关模块。
"""
import os
import sys

# 确保从 QuickForm 根目录运行
_quickform_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_quickform_root)
if _quickform_root not in sys.path:
    sys.path.insert(0, _quickform_root)

# 导入完整应用
from app import app

if __name__ == '__main__':
    import ssl
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    def _make_ssl_context():
        cert = os.path.join(_quickform_root, 'certs', 'quickform.cn.pem')
        key = os.path.join(_quickform_root, 'certs', 'quickform.cn.key')
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert, key)
            if hasattr(ssl, 'TLSVersion') and hasattr(ctx, 'minimum_version'):
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            return ctx
        except Exception:
            return (cert, key)

    port = int(os.environ.get('FLASK_PORT', '443'))
    logger.info("app_network 启动: 0.0.0.0:%d (HTTPS) - 完整应用（含数据库/AI/邮件）", port)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        use_reloader=False,
        threaded=True,
        ssl_context=_make_ssl_context(),
    )
