"""
管理后台路由 / Admin Routes
提供管理员功能的API接口
"""
from flask import Blueprint, request, jsonify, session, send_file, render_template, redirect, url_for
from flask_babel import gettext as _
from datetime import datetime
import os

from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.report import Report
from app.models.login_log import LoginLog
from app.services.customer_service import CustomerService
from app.services.report_service import ReportService
from app.utils.decorators import admin_required, manager_required, login_required, admin_page_required, login_page_required

admin_bp = Blueprint('admin', __name__)


# =============================================================================
# 管理员认证相关 / Admin Authentication
# =============================================================================

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    管理员登录 / Admin login
    只有管理员角色的用户才能登录管理后台
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': _('Username and password are required')
        }), 400
    
    user = User.query.filter_by(username=username).first()
    
    # 记录登录尝试
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    if user is None:
        LoginLog.log_login(None, ip_address, user_agent, success=False,
                          fail_reason='User not found')
        return jsonify({
            'success': False,
            'message': _('Invalid username or password')
        }), 401
    
    if not user.is_active:
        LoginLog.log_login(user, ip_address, user_agent, success=False,
                          fail_reason='Account disabled')
        return jsonify({
            'success': False,
            'message': _('Account has been disabled')
        }), 403
    
    # 检查是否为管理员
    if not (user.is_admin or user.role == 'admin'):
        LoginLog.log_login(user, ip_address, user_agent, success=False,
                          fail_reason='Not an admin')
        return jsonify({
            'success': False,
            'message': _('Admin privileges required')
        }), 403
    
    if not user.check_password(password):
        LoginLog.log_login(user, ip_address, user_agent, success=False,
                          fail_reason='Invalid password')
        return jsonify({
            'success': False,
            'message': _('Invalid username or password')
        }), 401
    
    # 登录成功
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['is_admin'] = True
    
    user.update_last_login()
    LoginLog.log_login(user, ip_address, user_agent, success=True)
    
    return jsonify({
        'success': True,
        'message': _('Admin login successful'),
        'user': user.to_dict()
    })


@admin_bp.route('/logout', methods=['GET', 'POST'])
@admin_required
def admin_logout():
    """管理员登出 / Admin logout"""
    user = request.current_user
    LoginLog.log_logout(user, request.remote_addr,
                       request.headers.get('User-Agent'))
    
    session.clear()
    
    # 如果是AJAX请求，返回JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': _('Logout successful')
        })
    
    # 如果是普通请求，重定向到登录页
    return redirect(url_for('auth.login_page'))


@admin_bp.route('/me')
@admin_required
def get_admin_info():
    """获取当前管理员信息 / Get current admin info"""
    return jsonify({
        'success': True,
        'user': request.current_user.to_dict()
    })


# =============================================================================
# 管理员仪表盘 / Admin Dashboard
# =============================================================================

@admin_bp.route('/dashboard')
@admin_page_required
def dashboard():
    """管理员仪表盘页面 / Admin dashboard page"""
    user = request.current_user
    
    # 获取统计数据
    total_customers = Customer.query.count()
    total_reports = Report.query.count()
    total_users = User.query.count()
    
    # 获取本月新增
    from datetime import datetime
    now = datetime.now()
    this_month_customers = Customer.query.filter(
        db.extract('year', Customer.created_at) == now.year,
        db.extract('month', Customer.created_at) == now.month
    ).count()
    
    # 获取最近上传的报表
    recent_reports = Report.query.order_by(Report.upload_date.desc()).limit(10).all()
    
    # 获取最近登录记录
    recent_logins = LoginLog.query.filter_by(success=True).order_by(LoginLog.login_time.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                           user=user,
                           total_customers=total_customers,
                           total_reports=total_reports,
                           total_users=total_users,
                           this_month_customers=this_month_customers,
                           recent_reports=recent_reports,
                           recent_logins=recent_logins)


# =============================================================================
# 客户管理 / Customer Management
# =============================================================================

@admin_bp.route('/customers', methods=['GET'])
@admin_required
def list_customers():
    """
    获取客户列表 / Get customer list
    支持分页、筛选和搜索
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    accountant_id = request.args.get('accountant_id', type=int)
    tax_type = request.args.get('tax_type')
    search = request.args.get('search')
    
    customers, total = CustomerService.list_customers(
        page=page,
        per_page=per_page,
        status=status,
        accountant_id=accountant_id,
        tax_type=tax_type,
        search=search
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [c.to_dict() for c in customers],
            'total': total,
            'page': page,
            'per_page': per_page
        }
    })


@admin_bp.route('/customers/<int:customer_id>', methods=['GET'])
@admin_required
def get_customer(customer_id):
    """获取客户详情 / Get customer details"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        return jsonify({
            'success': False,
            'message': _('Customer not found')
        }), 404
    
    return jsonify({
        'success': True,
        'data': customer.to_dict()
    })


@admin_bp.route('/customers', methods=['POST'])
@admin_required
def create_customer():
    """创建客户 / Create customer"""
    data = request.get_json() or {}
    
    # 添加创建人信息
    data['created_by'] = request.current_user.id
    
    customer, error = CustomerService.create_customer(data)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Customer created successfully'),
        'data': customer.to_dict()
    }), 201


@admin_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    """更新客户信息 / Update customer"""
    data = request.get_json() or {}
    
    customer, error = CustomerService.update_customer(customer_id, data)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Customer updated successfully'),
        'data': customer.to_dict()
    })


@admin_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@admin_required
def delete_customer(customer_id):
    """删除客户 / Delete customer"""
    success, error = CustomerService.delete_customer(customer_id)
    
    if not success:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Customer deleted successfully')
    })


@admin_bp.route('/customers/<int:customer_id>/status', methods=['PATCH'])
@admin_required
def update_customer_status(customer_id):
    """更新客户状态 / Update customer status"""
    data = request.get_json() or {}
    status = data.get('status')
    
    if not status:
        return jsonify({
            'success': False,
            'message': _('Status is required')
        }), 400
    
    customer, error = CustomerService.update_customer_status(customer_id, status)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Status updated successfully'),
        'data': customer.to_dict()
    })


@admin_bp.route('/customers/<int:customer_id>/assign-accountant', methods=['POST'])
@admin_required
def assign_accountant(customer_id):
    """分配负责会计 / Assign accountant to customer"""
    data = request.get_json() or {}
    accountant_id = data.get('accountant_id')
    
    if not accountant_id:
        return jsonify({
            'success': False,
            'message': _('Accountant ID is required')
        }), 400
    
    customer, error = CustomerService.assign_accountant(customer_id, accountant_id)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Accountant assigned successfully'),
        'data': customer.to_dict()
    })


@admin_bp.route('/customers/<int:customer_id>/reset-password', methods=['POST'])
@admin_required
def reset_customer_password(customer_id):
    """
    重置客户密码 / Reset customer password
    为客户生成新的登录密码
    """
    data = request.get_json() or {}
    new_password = data.get('new_password')
    
    if not new_password:
        # 如果没有提供新密码，生成随机密码
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    success, error = CustomerService.reset_customer_password(customer_id, new_password)
    
    if not success:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Password reset successfully'),
        'data': {
            'new_password': new_password  # 仅在生成随机密码时返回
        }
    })


@admin_bp.route('/customers/<int:customer_id>/create-login', methods=['POST'])
@admin_required
def create_customer_login(customer_id):
    """
    为客户创建登录账号 / Create login account for customer
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': _('Username and password are required')
        }), 400
    
    user, error = CustomerService.create_customer_login_account(
        customer_id=customer_id,
        username=username,
        password=password,
        email=email
    )
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Login account created successfully'),
        'data': user.to_dict()
    }), 201


@admin_bp.route('/customers/statistics', methods=['GET'])
@admin_required
def get_customer_statistics():
    """获取客户统计信息 / Get customer statistics"""
    stats = CustomerService.get_customer_statistics()
    
    return jsonify({
        'success': True,
        'data': stats
    })


@admin_bp.route('/customers/<int:customer_id>/reports', methods=['GET'])
@admin_required
def get_customer_reports(customer_id):
    """获取客户的报表列表 / Get customer's reports"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    reports, total = CustomerService.get_customer_reports(customer_id, page, per_page)
    
    return jsonify({
        'success': True,
        'data': {
            'items': [r.to_dict() for r in reports],
            'total': total,
            'page': page,
            'per_page': per_page
        }
    })


@admin_bp.route('/customers/bulk-action', methods=['POST'])
@admin_required
def customers_bulk_action():
    """客户批量操作 / Bulk action on customers"""
    data = request.get_json() or {}
    action = data.get('action')
    customer_ids = data.get('customer_ids', [])
    
    if not action or not customer_ids:
        return jsonify({
            'success': False,
            'message': _('Action and customer IDs are required')
        }), 400
    
    if action not in ['delete', 'activate', 'suspend', 'assign_accountant']:
        return jsonify({
            'success': False,
            'message': _('Invalid action')
        }), 400
    
    success_count = 0
    failed_count = 0
    
    for customer_id in customer_ids:
        try:
            if action == 'delete':
                success, error = CustomerService.delete_customer(customer_id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            elif action == 'activate':
                customer, error = CustomerService.update_customer_status(customer_id, 'active')
                if customer:
                    success_count += 1
                else:
                    failed_count += 1
            elif action == 'suspend':
                customer, error = CustomerService.update_customer_status(customer_id, 'suspended')
                if customer:
                    success_count += 1
                else:
                    failed_count += 1
            elif action == 'assign_accountant':
                accountant_id = data.get('accountant_id')
                if accountant_id:
                    customer, error = CustomerService.assign_accountant(customer_id, accountant_id)
                    if customer:
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
        except Exception as e:
            failed_count += 1
    
    return jsonify({
        'success': True,
        'message': _('Bulk action completed'),
        'data': {
            'action': action,
            'success_count': success_count,
            'failed_count': failed_count,
            'total': len(customer_ids)
        }
    })


# =============================================================================
# 报表管理 / Report Management
# =============================================================================

@admin_bp.route('/reports', methods=['GET'])
@admin_required
def list_reports():
    """获取报表列表 / Get report list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    customer_id = request.args.get('customer_id', type=int)
    report_type = request.args.get('report_type')
    status = request.args.get('status')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    reports, total = ReportService.list_reports(
        page=page,
        per_page=per_page,
        customer_id=customer_id,
        report_type=report_type,
        status=status,
        year=year,
        month=month
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [r.to_dict() for r in reports],
            'total': total,
            'page': page,
            'per_page': per_page
        }
    })


@admin_bp.route('/reports/<int:report_id>', methods=['GET'])
@admin_required
def get_report(report_id):
    """获取报表详情 / Get report details"""
    report = ReportService.get_report_by_id(report_id)
    if not report:
        return jsonify({
            'success': False,
            'message': _('Report not found')
        }), 404
    
    return jsonify({
        'success': True,
        'data': report.to_dict()
    })


@admin_bp.route('/reports', methods=['POST'])
@admin_required
def create_report():
    """创建报表 / Create report"""
    data = request.get_json() or {}
    
    # 添加创建人信息
    data['created_by'] = request.current_user.id
    
    report, error = ReportService.create_report(data)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report created successfully'),
        'data': report.to_dict()
    }), 201


@admin_bp.route('/reports/upload', methods=['POST'])
@admin_required
def upload_report():
    """
    上传报表文件 / Upload report file
    支持单文件上传
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': _('No file provided')
        }), 400
    
    file = request.files['file']
    
    # 获取表单数据
    customer_id = request.form.get('customer_id', type=int)
    report_name = request.form.get('report_name') or file.filename
    report_type = request.form.get('report_type')
    year = request.form.get('year', type=int)
    month = request.form.get('month', type=int)
    description = request.form.get('description')
    
    if not customer_id:
        return jsonify({
            'success': False,
            'message': _('Customer ID is required')
        }), 400
    
    if not report_type:
        return jsonify({
            'success': False,
            'message': _('Report type is required')
        }), 400
    
    if not year:
        return jsonify({
            'success': False,
            'message': _('Year is required')
        }), 400
    
    report, error = ReportService.upload_report(
        file=file,
        customer_id=customer_id,
        report_name=report_name,
        report_type=report_type,
        year=year,
        month=month,
        description=description,
        created_by=request.current_user.id
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report uploaded successfully'),
        'data': report.to_dict()
    }), 201


@admin_bp.route('/reports/batch-upload', methods=['POST'])
@admin_required
def batch_upload_reports():
    """
    批量上传报表 / Batch upload reports
    支持多文件同时上传
    """
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'message': _('No files provided')
        }), 400
    
    files = request.files.getlist('files')
    
    # 获取表单数据
    customer_id = request.form.get('customer_id', type=int)
    report_type = request.form.get('report_type')
    year = request.form.get('year', type=int)
    month = request.form.get('month', type=int)
    
    if not customer_id:
        return jsonify({
            'success': False,
            'message': _('Customer ID is required')
        }), 400
    
    if not report_type:
        return jsonify({
            'success': False,
            'message': _('Report type is required')
        }), 400
    
    if not year:
        return jsonify({
            'success': False,
            'message': _('Year is required')
        }), 400
    
    success_reports, failed_files = ReportService.batch_upload_reports(
        files=files,
        customer_id=customer_id,
        report_type=report_type,
        year=year,
        month=month,
        created_by=request.current_user.id
    )
    
    return jsonify({
        'success': True,
        'message': _('Batch upload completed'),
        'data': {
            'success_count': len(success_reports),
            'failed_count': len(failed_files),
            'success_reports': [r.to_dict() for r in success_reports],
            'failed_files': failed_files
        }
    })


@admin_bp.route('/reports/<int:report_id>', methods=['PUT'])
@admin_required
def update_report(report_id):
    """更新报表信息 / Update report"""
    data = request.get_json() or {}
    
    report, error = ReportService.update_report(report_id, data)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report updated successfully'),
        'data': report.to_dict()
    })


@admin_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@admin_required
def delete_report(report_id):
    """删除报表 / Delete report"""
    success, error = ReportService.delete_report(report_id)
    
    if not success:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report deleted successfully')
    })


@admin_bp.route('/reports/<int:report_id>/download', methods=['GET'])
@admin_required
def download_report(report_id):
    """下载报表文件 / Download report file"""
    file_path, error = ReportService.get_report_file_path(report_id)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    report = ReportService.get_report_by_id(report_id)
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=report.file_name
    )


@admin_bp.route('/reports/<int:report_id>/submit', methods=['POST'])
@admin_required
def submit_report(report_id):
    """提交报表 / Submit report"""
    report, error = ReportService.submit_report(report_id)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report submitted successfully'),
        'data': report.to_dict()
    })


@admin_bp.route('/reports/<int:report_id>/review', methods=['POST'])
@admin_required
def review_report(report_id):
    """审核报表 / Review report"""
    data = request.get_json() or {}
    approved = data.get('approved', True)
    
    report, error = ReportService.review_report(
        report_id=report_id,
        reviewer_id=request.current_user.id,
        approved=approved
    )
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report reviewed successfully'),
        'data': report.to_dict()
    })


@admin_bp.route('/reports/<int:report_id>/approve', methods=['POST'])
@admin_required
def approve_report(report_id):
    """批准报表 / Approve report"""
    report, error = ReportService.approve_report(report_id)
    
    if error:
        if 'not found' in error.lower():
            return jsonify({
                'success': False,
                'message': error
            }), 404
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': _('Report approved successfully'),
        'data': report.to_dict()
    })


@admin_bp.route('/reports/statistics', methods=['GET'])
@admin_required
def get_report_statistics():
    """获取报表统计信息 / Get report statistics"""
    stats = ReportService.get_report_statistics()
    
    return jsonify({
        'success': True,
        'data': stats
    })


@admin_bp.route('/customers/<int:customer_id>/report-statistics', methods=['GET'])
@admin_required
def get_customer_report_statistics(customer_id):
    """获取客户的报表统计 / Get customer's report statistics"""
    stats = ReportService.get_customer_report_statistics(customer_id)
    
    if not stats:
        return jsonify({
            'success': False,
            'message': _('Customer not found')
        }), 404
    
    return jsonify({
        'success': True,
        'data': stats
    })


# =============================================================================
# 用户管理 / User Management (Admin only)
# =============================================================================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """获取用户列表 / Get user list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
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
            'page': page,
            'per_page': per_page
        }
    })


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """获取用户详情 / Get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'success': True,
        'data': user.to_dict()
    })


@admin_bp.route('/users', methods=['POST'])
@admin_required
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


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
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


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户 / Delete user"""
    user = User.query.get_or_404(user_id)
    
    # 防止删除自己
    if user_id == request.current_user.id:
        return jsonify({
            'success': False,
            'message': _('Cannot delete yourself')
        }), 403
    
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


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """切换用户激活状态 / Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # 防止禁用自己
    if user_id == request.current_user.id:
        return jsonify({
            'success': False,
            'message': _('Cannot disable yourself')
        }), 403
    
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


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """重置用户密码 / Reset user password"""
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    
    new_password = data.get('new_password')
    if not new_password:
        # 生成随机密码
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Password reset successfully'),
        'data': {
            'new_password': new_password
        }
    })


@admin_bp.route('/users/roles', methods=['GET'])
@admin_required
def get_roles():
    """获取角色列表 / Get role list"""
    roles = [
        {'value': 'admin', 'label': _('Administrator'), 'description': _('Full system access')},
        {'value': 'manager', 'label': _('Manager'), 'description': _('Can manage accountants and customers')},
        {'value': 'accountant', 'label': _('Accountant'), 'description': _('Can manage assigned customers')},
        {'value': 'assistant', 'label': _('Assistant'), 'description': _('Limited access to assist accountants')}
    ]
    
    return jsonify({
        'success': True,
        'data': roles
    })


# =============================================================================
# 系统统计 / System Statistics
# =============================================================================

@admin_bp.route('/dashboard/statistics', methods=['GET'])
@admin_required
def get_dashboard_statistics():
    """获取仪表盘统计数据 / Get dashboard statistics"""
    # 客户统计
    customer_stats = CustomerService.get_customer_statistics()
    
    # 报表统计
    report_stats = ReportService.get_report_statistics()
    
    # 用户统计
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # 登录统计
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logins_today = LoginLog.query.filter(LoginLog.login_time >= today).count()
    
    # 最近登录的用户
    recent_logins = LoginLog.query.filter_by(action='login').order_by(
        LoginLog.login_time.desc()
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': {
            'customers': customer_stats,
            'reports': report_stats,
            'users': {
                'total': total_users,
                'active': active_users
            },
            'logins_today': logins_today,
            'recent_logins': [log.to_dict() for log in recent_logins]
        }
    })


# =============================================================================
# 登录日志 / Login Logs
# =============================================================================

@admin_bp.route('/login-logs', methods=['GET'])
@admin_required
def get_login_logs():
    """获取登录日志 / Get login logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    
    query = LoginLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action:
        query = query.filter_by(action=action)
    
    pagination = query.order_by(LoginLog.login_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


# =============================================================================
# 页面路由 / Page Routes
# =============================================================================

@admin_bp.route('/upload-page')
@admin_page_required
def upload_page():
    """报表上传页面 / Report upload page"""
    # 获取所有客户列表
    all_customers = Customer.query.all()
    
    # 获取报表类型选项
    report_types = [
        {'id': 'balance_sheet', 'name': '资产负债表'},
        {'id': 'income_statement', 'name': '利润表'},
        {'id': 'cash_flow', 'name': '现金流量表'},
        {'id': 'tax_return', 'name': '纳税申报表'},
        {'id': 'general_ledger', 'name': '总账'},
        {'id': 'detail_ledger', 'name': '明细账'},
        {'id': 'bank_statement', 'name': '银行对账单'},
        {'id': 'other', 'name': '其他'}
    ]
    
    # 获取可用年份
    current_year = datetime.now().year
    available_years = list(range(current_year - 2, current_year + 3))
    
    # 获取预选择的客户ID（如果有）
    preselected_customer_id = request.args.get('customer_id', type=int)
    
    return render_template('admin/upload.html',
                           all_customers=all_customers,
                           report_types=report_types,
                           available_years=available_years,
                           current_year=current_year,
                           current_month=datetime.now().month,
                           preselected_customer_id=preselected_customer_id)


@admin_bp.route('/reports-page')
@admin_page_required
def reports_page():
    """报表管理页面 / Reports management page"""
    # 获取所有客户列表（用于筛选）
    all_customers = Customer.query.all()
    
    # 获取报表类型选项
    report_types = [
        {'id': 'balance_sheet', 'name': '资产负债表'},
        {'id': 'income_statement', 'name': '利润表'},
        {'id': 'cash_flow', 'name': '现金流量表'},
        {'id': 'tax_return', 'name': '纳税申报表'},
        {'id': 'general_ledger', 'name': '总账'},
        {'id': 'detail_ledger', 'name': '明细账'},
        {'id': 'bank_statement', 'name': '银行对账单'},
        {'id': 'other', 'name': '其他'}
    ]
    
    # 获取状态选项
    status_options = [
        {'id': 'draft', 'name': '草稿'},
        {'id': 'submitted', 'name': '已提交'},
        {'id': 'reviewed', 'name': '已审核'},
        {'id': 'approved', 'name': '已批准'},
        {'id': 'archived', 'name': '已归档'}
    ]
    
    return render_template('admin/reports.html',
                           all_customers=all_customers,
                           report_types=report_types,
                           status_options=status_options)


@admin_bp.route('/customers-page')
@admin_page_required
def customers_page():
    """客户管理页面 / Customers management page"""
    # 获取所有会计用户（用于分配）
    accountants = User.query.filter(
        db.or_(User.role == 'accountant', User.role == 'manager')
    ).all()
    
    # 获取统计信息
    stats = CustomerService.get_customer_statistics()
    
    return render_template('admin/customers.html',
                           accountants=accountants,
                           stats=stats)


@admin_bp.route('/customers/<int:customer_id>/detail')
@admin_required
def customer_detail_page(customer_id):
    """客户详情页面 / Customer detail page"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        return render_template('admin/error.html', message='客户不存在'), 404
    
    # 获取客户的报表统计
    report_stats = ReportService.get_customer_report_statistics(customer_id)
    
    # 获取客户的登录用户
    login_user = User.query.filter_by(
        id=customer.user_id
    ).first() if customer.user_id else None
    
    return render_template('admin/customer_detail.html',
                           customer=customer,
                           report_stats=report_stats,
                           login_user=login_user)


@admin_bp.route('/customers/create')
@admin_required
def customer_create_page():
    """创建客户页面 / Create customer page"""
    # 获取所有会计用户
    accountants = User.query.filter(
        db.or_(User.role == 'accountant', User.role == 'manager')
    ).all()
    
    return render_template('admin/customer_form.html',
                           accountants=accountants,
                           customer=None,
                           mode='create')


@admin_bp.route('/customers/<int:customer_id>/edit')
@admin_required
def customer_edit_page(customer_id):
    """编辑客户页面 / Edit customer page"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        return render_template('admin/error.html', message='客户不存在'), 404
    
    # 获取所有会计用户
    accountants = User.query.filter(
        db.or_(User.role == 'accountant', User.role == 'manager')
    ).all()
    
    return render_template('admin/customer_form.html',
                           accountants=accountants,
                           customer=customer,
                           mode='edit')


@admin_bp.route('/settings')
@admin_page_required
def settings_page():
    """系统设置页面 / System settings page"""
    # 获取系统配置信息
    from flask import current_app
    
    config_info = {
        'app_name': current_app.config.get('APP_NAME', '代理记账客户管理系统'),
        'debug_mode': current_app.debug,
        'upload_max_size': current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) // (1024 * 1024),  # MB
        'allowed_extensions': current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}),
        'session_lifetime': current_app.config.get('PERMANENT_SESSION_LIFETIME'),
        'database_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('://', '://***:***@') if '://' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'
    }
    
    # 获取用户统计
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    
    return render_template('admin/settings.html',
                           config=config_info,
                           total_users=total_users,
                           active_users=active_users,
                           admin_users=admin_users)


@admin_bp.route('/logs')
@admin_page_required
def logs_page():
    """系统日志页面 / System logs page"""
    # 获取登录日志
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 查询登录日志
    logs_query = LoginLog.query.order_by(LoginLog.login_time.desc())
    
    # 分页
    pagination = logs_query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    
    # 获取统计信息
    total_logs = LoginLog.query.count()
    success_logs = LoginLog.query.filter_by(success=True).count()
    failed_logs = LoginLog.query.filter_by(success=False).count()
    
    # 获取今日登录数
    from datetime import datetime, timedelta
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = LoginLog.query.filter(LoginLog.login_time >= today).count()
    
    return render_template('admin/logs.html',
                           logs=logs,
                           pagination=pagination,
                           total_logs=total_logs,
                           success_logs=success_logs,
                           failed_logs=failed_logs,
                           today_logs=today_logs,
                           page=page,
                           per_page=per_page)
