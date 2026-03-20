"""
JWT 认证工具 / JWT Authentication Utilities
用于 React 前端与 Flask API 的认证集成
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_babel import gettext as _

from app.models.user import User


def generate_token(user_id, username, role='user'):
    """
    生成 JWT Token
    
    Args:
        user_id: 用户 ID
        username: 用户名
        role: 用户角色
    
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def verify_token(token):
    """
    验证 JWT Token
    
    Args:
        token: JWT token
    
    Returns:
        dict: token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    JWT Token 认证装饰器
    
    使用方式:
    @api_bp.route('/protected')
    @token_required
    def protected_route():
        return jsonify({'user_id': g.current_user.id})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从 Authorization header 获取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': _('Invalid token format')
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': _('Token is missing')
            }), 401
        
        # 验证 token
        payload = verify_token(token)
        if payload is None:
            return jsonify({
                'success': False,
                'message': _('Token is invalid or expired')
            }), 401
        
        # 获取用户信息
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': _('User not found')
            }), 401
        
        # 将用户信息存入 Flask g 对象
        g.current_user = user
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    管理员权限装饰器
    
    使用方式:
    @api_bp.route('/admin-only')
    @token_required
    @admin_required
    def admin_only_route():
        return jsonify({'message': 'Admin access'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': _('Admin access required')
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    可选 Token 装饰器
    
    如果提供了有效 token 则认证，否则允许匿名访问
    
    使用方式:
    @api_bp.route('/public-or-private')
    @optional_token
    def public_or_private_route():
        if hasattr(g, 'current_user'):
            return jsonify({'user': g.current_user.username})
        else:
            return jsonify({'message': 'Anonymous'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass
        
        if token:
            payload = verify_token(token)
            if payload:
                user = User.query.get(payload['user_id'])
                if user:
                    g.current_user = user
                    g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated
