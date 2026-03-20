"""
登录日志模型 / Login Log Model
"""
from datetime import datetime
from . import db


class LoginLog(db.Model):
    """
    登录日志模型 - 记录用户登录和登出操作
    Login Log Model - Record user login and logout operations
    """
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 关联用户 / Associated User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    username = db.Column(db.String(80), nullable=False, comment='用户名（冗余存储）')
    
    # 操作类型 / Operation Type
    # login-登录, logout-登出, login_failed-登录失败
    action = db.Column(db.String(20), nullable=False, index=True, comment='操作类型')
    
    # 客户端信息 / Client Information
    ip_address = db.Column(db.String(45), nullable=True, comment='IP地址')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理（浏览器信息）')
    
    # 设备信息 / Device Information
    device_type = db.Column(db.String(50), nullable=True, comment='设备类型')
    browser = db.Column(db.String(100), nullable=True, comment='浏览器')
    os = db.Column(db.String(100), nullable=True, comment='操作系统')
    
    # 登录结果 / Login Result
    success = db.Column(db.Boolean, default=True, nullable=False, comment='是否成功')
    fail_reason = db.Column(db.String(200), nullable=True, comment='失败原因')
    location = db.Column(db.String(200), nullable=True, comment='地理位置')
    
    # 时间戳 / Timestamp
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True, comment='操作时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True, comment='创建时间')
    
    def __repr__(self):
        return f'<LoginLog {self.username} {self.action}>'
    
    def get_action_display(self):
        """获取操作类型显示文本 / Get action type display text"""
        action_map = {
            'login': '登录',
            'logout': '登出',
            'login_failed': '登录失败'
        }
        return action_map.get(self.action, self.action)
    
    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'action_display': self.get_action_display(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'success': self.success,
            'fail_reason': self.fail_reason,
            'location': self.location,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def log_login(user, ip_address=None, user_agent=None, success=True, fail_reason=None, location=None):
        """
        记录登录日志 / Record login log
        
        Args:
            user: User model instance
            ip_address: Client IP address
            user_agent: Client user agent string
            success: Whether login was successful
            fail_reason: Reason for login failure if applicable
            location: Geographical location
        """
        log = LoginLog(
            user_id=user.id if user else None,
            username=user.username if user else 'unknown',
            action='login' if success else 'login_failed',
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            fail_reason=fail_reason,
            location=location,
            login_time=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_logout(user, ip_address=None, user_agent=None):
        """
        记录登出日志 / Record logout log
        
        Args:
            user: User model instance
            ip_address: Client IP address
            user_agent: Client user agent string
        """
        log = LoginLog(
            user_id=user.id if user else None,
            username=user.username if user else 'unknown',
            action='logout',
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            login_time=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def get_recent_logins(user_id=None, limit=10):
        """
        获取最近登录记录 / Get recent login records
        
        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum number of records to return
        """
        query = LoginLog.query.filter(LoginLog.action.in_(['login', 'login_failed']))
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.order_by(LoginLog.login_time.desc()).limit(limit).all()
