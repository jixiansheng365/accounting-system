"""
代理记账客户管理系统 - 应用工厂
Accounting Customer Management System - Application Factory
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session
from flask_babel import Babel, gettext as _
from flask_cors import CORS

from config import config
from app.models import db

# 初始化 Babel
babel = Babel()

# 初始化 CORS
cors = CORS()


def create_app(config_name=None):
    """
    应用工厂函数 / Application factory function
    
    Args:
        config_name: 配置名称 (development, production, testing)
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config.get(config_name, config['default']))
    
    # 确保数据目录存在
    _ensure_directories(app)
    
    # 初始化扩展
    _init_extensions(app)
    
    # 注册蓝图
    _register_blueprints(app)
    
    # 配置日志
    _configure_logging(app)
    
    # 注册模板全局函数
    _register_template_globals(app)
    
    # 注册错误处理
    _register_error_handlers(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


def _ensure_directories(app):
    """确保必要的目录存在 / Ensure necessary directories exist"""
    dirs_to_create = [
        os.path.join(app.root_path, '..', 'data'),
        os.path.join(app.root_path, '..', 'logs'),
        os.path.join(app.root_path, '..', 'uploads'),
    ]
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)


def _init_extensions(app):
    """初始化 Flask 扩展 / Initialize Flask extensions"""
    # 初始化 SQLAlchemy
    db.init_app(app)
    
    # 初始化 Babel
    babel.init_app(app, locale_selector=get_locale)
    
    # 初始化 CORS - 允许 React 前端访问
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/auth/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })


def get_locale():
    """
    获取当前语言 / Get current locale
    
    优先级:
    1. 用户 session 中的语言设置（最高优先级）
    2. URL 参数中的 lang
    3. 浏览器 Accept-Language 头
    4. 默认语言 (简体中文)
    """
    # 支持的语言列表 (使用Babel标准locale标识符)
    supported_langs = ['zh_Hans_CN', 'zh_Hant_TW', 'ja', 'en', 'ko']
    lang_mapping = {
        'zh_CN': 'zh_Hans_CN',
        'zh_TW': 'zh_Hant_TW',
        'ja': 'ja',
        'en': 'en',
        'ko': 'ko'
    }
    
    # 获取存储的语言代码
    stored_lang = None
    if 'lang' in session:
        stored_lang = session['lang']
    else:
        # 检查 URL 参数
        lang = request.args.get('lang')
        if lang in lang_mapping:
            session['lang'] = lang
            stored_lang = lang
    
    # 映射到Babel标准locale
    if stored_lang and stored_lang in lang_mapping:
        return lang_mapping[stored_lang]
    
    # 3. 检查浏览器语言
    browser_lang = request.accept_languages.best_match(['zh-CN', 'zh-TW', 'zh', 'ja', 'en', 'ko'])
    if browser_lang == 'zh-CN' or browser_lang == 'zh':
        session['lang'] = 'zh_CN'
        return 'zh_Hans_CN'
    elif browser_lang == 'zh-TW':
        session['lang'] = 'zh_TW'
        return 'zh_Hant_TW'
    elif browser_lang == 'ja':
        session['lang'] = 'ja'
        return 'ja'
    elif browser_lang == 'en':
        session['lang'] = 'en'
        return 'en'
    elif browser_lang == 'ko':
        session['lang'] = 'ko'
        return 'ko'
    
    # 4. 默认语言为简体中文
    return 'zh_Hans_CN'


def _register_blueprints(app):
    """注册 Flask 蓝图 / Register Flask blueprints"""
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.customers import customers_bp
    from app.routes.reports import reports_bp
    from app.routes.users import users_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def _configure_logging(app):
    """配置日志 / Configure logging"""
    if not app.debug:
        # 文件日志
        log_file = app.config.get('LOG_FILE')
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=1024 * 1024 * 10,  # 10MB
                backupCount=10
            )
            file_handler.setLevel(
                getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(file_handler)
        
        # 控制台日志
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        app.logger.addHandler(stream_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Accounting system startup')


def _register_template_globals(app):
    """注册模板全局函数 / Register template global functions"""
    
    @app.context_processor
    def inject_globals():
        """注入模板全局变量 / Inject template global variables"""
        return {
            'app_name': _('Accounting Customer Management System'),
            'app_version': '1.0.0',
        }


def _register_error_handlers(app):
    """注册错误处理器 / Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {request.url}')
        return {'error': 'Not found', 'message': str(error)}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'500 error: {str(error)}')
        return {'error': 'Internal server error', 'message': str(error)}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'403 error: {request.url}')
        return {'error': 'Forbidden', 'message': str(error)}, 403
