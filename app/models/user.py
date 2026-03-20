"""
用户模型 / User Model
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    """
    用户模型 - 系统用户（代理记账公司员工）
    User Model - System users (accounting firm employees)
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True, comment='邮箱')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    real_name = db.Column(db.String(50), nullable=True, comment='真实姓名')
    phone = db.Column(db.String(20), nullable=True, comment='电话')
    
    # 用户角色: admin-管理员, manager-主管, accountant-会计, assistant-助理
    role = db.Column(db.String(20), default='accountant', nullable=False, comment='用户角色')
    
    # 用户状态
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='是否激活')
    is_admin = db.Column(db.Boolean, default=False, nullable=False, comment='是否超级管理员')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    last_login_at = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    
    # 关联关系
    customers = db.relationship('Customer', backref='accountant', lazy='dynamic', 
                                foreign_keys='Customer.accountant_id')
    login_logs = db.relationship('LoginLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """设置密码 / Set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码 / Check password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间 / Update last login time"""
        self.last_login_at = datetime.utcnow()
        db.session.commit()
    
    def has_role(self, role):
        """检查用户是否有指定角色 / Check if user has specific role"""
        return self.role == role or self.is_admin
    
    def can_manage_user(self, user):
        """检查是否可以管理其他用户 / Check if can manage other users"""
        if self.is_admin:
            return True
        if self.role == 'manager' and user.role in ['accountant', 'assistant']:
            return True
        return False
    
    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
