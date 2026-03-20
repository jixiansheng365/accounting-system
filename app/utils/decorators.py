"""
权限装饰器 / Permission Decorators
"""
from functools import wraps
from flask import session, jsonify, request, redirect, url_for
from flask_babel import gettext as _

from app.models.user import User
from app.models.customer import Customer


def login_required(f):
    """
    登录验证装饰器 / Login required decorator
    确保用户已登录
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': _('Authentication required. Please login.')
            }), 401
        
        # 将当前用户添加到请求上下文
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': _('User not found. Please login again.')
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled.')
            }), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    管理员权限装饰器 / Admin required decorator
    确保用户是管理员角色
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': _('Authentication required. Please login.')
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': _('User not found. Please login again.')
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled.')
            }), 403
        
        # 检查是否为管理员
        if not (user.is_admin or user.role == 'admin'):
            return jsonify({
                'success': False,
                'message': _('Admin privileges required.')
            }), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def manager_required(f):
    """
    主管及以上权限装饰器 / Manager required decorator
    允许管理员和主管访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': _('Authentication required. Please login.')
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': _('User not found. Please login again.')
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled.')
            }), 403
        
        # 检查权限等级
        allowed_roles = ['admin', 'manager']
        if not (user.is_admin or user.role in allowed_roles):
            return jsonify({
                'success': False,
                'message': _('Manager privileges required.')
            }), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def accountant_required(f):
    """
    会计及以上权限装饰器 / Accountant required decorator
    允许管理员、主管和会计访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': _('Authentication required. Please login.')
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': _('User not found. Please login again.')
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled.')
            }), 403
        
        # 检查权限等级
        allowed_roles = ['admin', 'manager', 'accountant']
        if not (user.is_admin or user.role in allowed_roles):
            return jsonify({
                'success': False,
                'message': _('Insufficient privileges.')
            }), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def customer_owner_or_admin(f):
    """
    客户所有者或管理员权限装饰器 / Customer owner or admin decorator
    确保用户是客户本人或管理员
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': _('Authentication required. Please login.')
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': _('User not found. Please login again.')
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled.')
            }), 403
        
        # 管理员可以访问所有客户
        if user.is_admin or user.role == 'admin':
            request.current_user = user
            return f(*args, **kwargs)
        
        # 检查是否是客户本人
        customer_id = kwargs.get('customer_id')
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer and customer.user_id == user_id:
                request.current_user = user
                return f(*args, **kwargs)
        
        # 检查是否是负责该客户的会计
        customer_id = kwargs.get('customer_id')
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer and customer.accountant_id == user_id:
                request.current_user = user
                return f(*args, **kwargs)
        
        return jsonify({
            'success': False,
            'message': _('Permission denied. You do not have access to this customer.')
        }), 403
    
    return decorated_function


def role_required(*roles):
    """
    指定角色权限装饰器 / Role required decorator
    允许指定角色的用户访问
    
    Args:
        *roles: 允许的角色列表，如 'admin', 'manager', 'accountant', 'assistant'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': _('Authentication required. Please login.')
                }), 401
            
            user = User.query.get(user_id)
            if not user:
                session.clear()
                return jsonify({
                    'success': False,
                    'message': _('User not found. Please login again.')
                }), 401
            
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'message': _('Account has been disabled.')
                }), 403
            
            # 检查角色权限
            allowed_roles = list(roles)
            if not (user.is_admin or user.role in allowed_roles):
                return jsonify({
                    'success': False,
                    'message': _('Insufficient privileges. Required roles: {}').format(', '.join(roles))
                }), 403
            
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# =============================================================================
# 页面路由专用装饰器 / Page Route Decorators
# 用于渲染页面的路由，未登录时重定向到登录页面而不是返回JSON
# =============================================================================

def admin_page_required(f):
    """
    管理员页面权限装饰器 / Admin page required decorator
    用于页面路由，未登录时重定向到登录页面
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        lang = session.get('lang', 'zh_CN')
        
        if not user_id:
            return redirect(url_for('auth.login_page', lang=lang))
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login_page', lang=lang))
        
        if not user.is_active:
            return redirect(url_for('auth.login_page', lang=lang))
        
        # 检查是否为管理员
        if not (user.is_admin or user.role == 'admin'):
            return redirect(url_for('main.dashboard', lang=lang))
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def login_page_required(f):
    """
    登录页面权限装饰器 / Login page required decorator
    用于页面路由，未登录时重定向到登录页面
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        lang = session.get('lang', 'zh_CN')
        
        if not user_id:
            return redirect(url_for('auth.login_page', lang=lang))
        
        user = User.query.get(user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login_page', lang=lang))
        
        if not user.is_active:
            return redirect(url_for('auth.login_page', lang=lang))
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function
