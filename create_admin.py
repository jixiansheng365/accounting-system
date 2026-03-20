#!/usr/bin/env python3
"""创建管理员账号"""
import os
import sys

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
os.environ['DATABASE_URL'] = 'sqlite:////opt/accounting-system/data/accounting.db'

# 添加项目路径
sys.path.insert(0, '/opt/accounting-system')

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app('production')

with app.app_context():
    # 检查是否已存在admin用户
    admin = User.query.filter_by(username='admin').first()
    if admin:
        # 重置密码
        admin.password_hash = generate_password_hash('Test@123456')
        db.session.commit()
        print('管理员密码已重置为: Test@123456')
    else:
        # 创建新管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('Test@123456'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员账号创建成功!')
        print('用户名: admin')
        print('密码: Test@123456')
