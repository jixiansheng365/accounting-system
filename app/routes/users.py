"""
用户管理路由 / User Management Routes
"""
from flask import Blueprint, request, jsonify
from flask_babel import gettext as _

from app.models import db
from app.models.user import User
from app.models.login_log import LoginLog

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
def list_users():
    """获取用户列表 / Get user list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 筛选参数
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)
    search = request.args.get('search')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.real_name.contains(search)
            )
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    })


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户详情 / Get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'success': True,
        'data': user.to_dict()
    })


@users_bp.route('/', methods=['POST'])
def create_user():
    """创建用户 / Create user"""
    data = request.get_json() or {}
    
    # 必填字段验证
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': _('{} is required').format(field)
            }), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'success': False,
            'message': _('Username already exists')
        }), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'success': False,
            'message': _('Email already exists')
        }), 400
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        real_name=data.get('real_name'),
        phone=data.get('phone'),
        role=data.get('role', 'accountant'),
        is_active=data.get('is_active', True),
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('User created successfully'),
        'data': user.to_dict()
    }), 201


@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息 / Update user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    
    # 更新字段
    fields = ['email', 'real_name', 'phone', 'role', 'is_active', 'is_admin']
    
    for field in fields:
        if field in data:
            setattr(user, field, data[field])
    
    # 单独处理密码更新
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('User updated successfully'),
        'data': user.to_dict()
    })


@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户 / Delete user"""
    user = User.query.get_or_404(user_id)
    
    # 防止删除超级管理员
    if user.is_admin:
        return jsonify({
            'success': False,
            'message': _('Cannot delete admin user')
        }), 403
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('User deleted successfully')
    })


@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    """切换用户激活状态 / Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # 防止禁用超级管理员
    if user.is_admin:
        return jsonify({
            'success': False,
            'message': _('Cannot disable admin user')
        }), 403
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({
        'success': True,
        'message': _('User {} successfully').format(status),
        'data': user.to_dict()
    })


@users_bp.route('/<int:user_id>/login-logs', methods=['GET'])
def get_user_login_logs(user_id):
    """获取用户登录日志 / Get user login logs"""
    user = User.query.get_or_404(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = LoginLog.query.filter_by(user_id=user_id).order_by(
        LoginLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': {
            'items': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    })


@users_bp.route('/roles', methods=['GET'])
def get_roles():
    """获取角色列表 / Get role list"""
    roles = [
        {'value': 'admin', 'label': _('Role Admin')},
        {'value': 'manager', 'label': _('Role Manager')},
        {'value': 'accountant', 'label': _('Role Accountant')},
        {'value': 'assistant', 'label': _('Role Assistant')}
    ]
    
    return jsonify({
        'success': True,
        'data': roles
    })


@users_bp.route('/statistics', methods=['GET'])
def get_user_statistics():
    """获取用户统计信息 / Get user statistics"""
    total = User.query.count()
    active = User.query.filter_by(is_active=True).count()
    inactive = User.query.filter_by(is_active=False).count()
    
    # 按角色统计
    by_role = {}
    for role in ['admin', 'manager', 'accountant', 'assistant']:
        count = User.query.filter_by(role=role).count()
        by_role[role] = count
    
    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'active': active,
            'inactive': inactive,
            'by_role': by_role
        }
    })
