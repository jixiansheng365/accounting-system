"""
认证路由 / Authentication Routes
"""
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, current_app
from flask_babel import gettext as _
import datetime

from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.login_log import LoginLog
from app.utils.jwt_auth import generate_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET'])
def login_page():
    """登录页面 / Login page"""
    # 处理语言参数
    lang = request.args.get('lang')
    supported_langs = ['zh_CN', 'zh_TW', 'ja', 'en', 'ko']
    if lang and lang in supported_langs:
        session['lang'] = lang
    elif 'lang' not in session:
        session['lang'] = 'zh_CN'
    
    if session.get('user_id'):
        return redirect(url_for('main.dashboard', lang=session.get('lang', 'zh_CN')))
    
    last_login = None
    username = session.get('last_username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            last_login = LoginLog.query.filter_by(user_id=user.id, success=True).order_by(LoginLog.login_time.desc()).first()
    
    return render_template('auth/login.html', last_login=last_login)


@auth_bp.route('/logout')
def logout_page():
    """登出页面 / Logout page"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            LoginLog.log_logout(user, request.remote_addr, 
                               request.headers.get('User-Agent'))
    
    session.clear()
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 / User login"""
    # 支持 JSON 和表单两种提交方式
    if request.is_json:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    
    if not username or not password:
        if request.is_json:
            return jsonify({
                'success': False,
                'message': _('Username and password are required')
            }), 400
        else:
            return render_template('auth/login.html', error=_('Username and password are required')), 400
    
    user = User.query.filter_by(username=username).first()
    
    # 记录登录尝试
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    if user is None:
        LoginLog.log_login(None, ip_address, user_agent, success=False, 
                          fail_reason='User not found')
        if request.is_json:
            return jsonify({
                'success': False,
                'message': _('Invalid username or password')
            }), 401
        else:
            return render_template('auth/login.html', error=_('Invalid username or password')), 401
    
    if not user.is_active:
        LoginLog.log_login(user, ip_address, user_agent, success=False,
                          fail_reason='Account disabled')
        if request.is_json:
            return jsonify({
                'success': False,
                'message': _('Account has been disabled')
            }), 403
        else:
            return render_template('auth/login.html', error=_('Account has been disabled')), 403
    
    if not user.check_password(password):
        LoginLog.log_login(user, ip_address, user_agent, success=False,
                          fail_reason='Invalid password')
        if request.is_json:
            return jsonify({
                'success': False,
                'message': _('Invalid username or password')
            }), 401
        else:
            return render_template('auth/login.html', error=_('Invalid username or password')), 401
    
    # 登录成功
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    user.update_last_login()
    LoginLog.log_login(user, ip_address, user_agent, success=True)
    
    if request.is_json:
        return jsonify({
            'success': True,
            'message': _('Login successful'),
            'user': user.to_dict(),
            'token': generate_token(user.id, user.username, user.role),
            'expires_in': 86400  # 24 hours in seconds
        })
    else:
        # 表单提交成功后重定向到仪表板，保留语言设置
        lang = session.get('lang', 'zh_CN')
        return redirect(url_for('main.dashboard', lang=lang))


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出 / User logout"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            LoginLog.log_logout(user, request.remote_addr, 
                               request.headers.get('User-Agent'))
    
    session.clear()
    return jsonify({
        'success': True,
        'message': _('Logout successful')
    })


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册 / User registration (admin only in production)"""
    data = request.get_json() or {}
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({
            'success': False,
            'message': _('Username, email and password are required')
        }), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({
            'success': False,
            'message': _('Username already exists')
        }), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'message': _('Email already exists')
        }), 400
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        real_name=data.get('real_name'),
        phone=data.get('phone'),
        role=data.get('role', 'accountant')
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Registration successful'),
        'user': user.to_dict()
    }), 201


@auth_bp.route('/me')
def get_current_user():
    """获取当前登录用户信息 / Get current user info"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'message': _('Not logged in')
        }), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'message': _('User not found')
        }), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码 / Change password"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'message': _('Not logged in')
        }), 401
    
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({
            'success': False,
            'message': _('Old password and new password are required')
        }), 400
    
    user = User.query.get(user_id)
    if not user.check_password(old_password):
        return jsonify({
            'success': False,
            'message': _('Invalid old password')
        }), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Password changed successfully')
    })
