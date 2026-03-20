#!/usr/bin/env python3
"""初始化数据库脚本"""
import os
import sys

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
os.environ['DATABASE_URL'] = 'sqlite:////opt/accounting-system/data/accounting.db'

# 添加项目路径
sys.path.insert(0, '/opt/accounting-system')

from app import create_app
from app.models import db

app = create_app('production')

with app.app_context():
    db.create_all()
    print('数据库初始化完成')
