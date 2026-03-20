"""
模型模块初始化文件
Models module initialization
"""
from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()

# 导入所有模型，方便从 models 包统一导入
from .user import User
from .customer import Customer
from .report import Report
from .login_log import LoginLog

__all__ = ['db', 'User', 'Customer', 'Report', 'LoginLog']
