"""
代理记账客户管理系统配置文件
Configuration file for Accounting Customer Management System
"""
import os
from datetime import timedelta

# 获取项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置类 / Base configuration class"""
    
    # 密钥配置 / Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # 数据库配置 / Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data', 'accounting.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设置为 True 可查看 SQL 语句
    
    # 分页配置 / Pagination
    ITEMS_PER_PAGE = 20
    
    # 会话配置 / Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # 文件上传配置 / File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}
    
    # 多语言配置 / Internationalization
    BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
    BABEL_SUPPORTED_LOCALES = ['zh_Hans_CN', 'zh_Hant_TW', 'ja', 'en', 'ko']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, 'app', 'translations')
    
    # 日志配置 / Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
    
    # 时区配置 / Timezone
    TIMEZONE = 'Asia/Shanghai'


class DevelopmentConfig(Config):
    """开发环境配置 / Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置 / Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境必须使用环境变量设置的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """测试环境配置 / Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# 配置映射 / Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
