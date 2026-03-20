"""
API 路由 - RESTful API 接口
API Routes - RESTful API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_babel import gettext as _

from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.report import Report
from app.models.login_log import LoginLog
from app.utils.jwt_auth import token_required, optional_token

api_bp = Blueprint('api', __name__)


# ==================== 仪表盘 API ====================
@api_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    """仪表盘数据 / Dashboard data"""
    # 客户统计
    total_customers = Customer.query.count()
    active_customers = Customer.query.filter_by(status='active').count()
    
    # 报表统计
    total_reports = Report.query.count()
    pending_reports = Report.query.filter(Report.status.in_(['draft', 'submitted'])).count()
    
    # 用户统计
    total_users = User.query.filter_by(is_active=True).count()
    
    # 最近活动
    recent_logs = LoginLog.query.order_by(LoginLog.created_at.desc()).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': {
            'statistics': {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'total_users': total_users
            },
            'recent_activity': [log.to_dict() for log in recent_logs]
        }
    })


# ==================== 客户 API ====================
@api_bp.route('/customers', methods=['GET'])
@token_required
def api_list_customers():
    """API: 获取客户列表 / Get customer list"""
    return _paginate_query(Customer.query.order_by(Customer.created_at.desc()))


@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@token_required
def api_get_customer(customer_id):
    """API: 获取客户详情 / Get customer details"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({'success': True, 'data': customer.to_dict()})


@api_bp.route('/customers', methods=['POST'])
@token_required
def api_create_customer(customer_id):
    """API: 创建客户 / Create customer"""
    data = request.get_json() or {}
    
    if not data.get('company_name'):
        return jsonify({'success': False, 'message': _('Company name is required')}), 400
    
    customer = Customer(**{k: v for k, v in data.items() 
                          if hasattr(Customer, k)})
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({'success': True, 'data': customer.to_dict()}), 201


@api_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@token_required
def api_update_customer(customer_id):
    """API: 更新客户 / Update customer"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}
    
    for key, value in data.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()})


@api_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@token_required
def api_delete_customer(customer_id):
    """API: 删除客户 / Delete customer"""
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'success': True, 'message': _('Customer deleted')})


# ==================== 报表 API ====================
@api_bp.route('/reports', methods=['GET'])
@token_required
def api_list_reports():
    """API: 获取报表列表 / Get report list"""
    return _paginate_query(Report.query.order_by(Report.created_at.desc()))


@api_bp.route('/reports/<int:report_id>', methods=['GET'])
@token_required
def api_get_report(report_id):
    """API: 获取报表详情 / Get report details"""
    report = Report.query.get_or_404(report_id)
    return jsonify({'success': True, 'data': report.to_dict()})


@api_bp.route('/reports', methods=['POST'])
@token_required
def api_create_report():
    """API: 创建报表 / Create report"""
    data = request.get_json() or {}
    
    report = Report(**{k: v for k, v in data.items() 
                      if hasattr(Report, k)})
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'success': True, 'data': report.to_dict()}), 201


@api_bp.route('/reports/<int:report_id>', methods=['PUT'])
@token_required
def api_update_report(report_id):
    """API: 更新报表 / Update report"""
    report = Report.query.get_or_404(report_id)
    data = request.get_json() or {}
    
    for key, value in data.items():
        if hasattr(report, key):
            setattr(report, key, value)
    
    db.session.commit()
    return jsonify({'success': True, 'data': report.to_dict()})


@api_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@token_required
def api_delete_report(report_id):
    """API: 删除报表 / Delete report"""
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({'success': True, 'message': _('Report deleted')})


# ==================== 用户 API ====================
@api_bp.route('/users', methods=['GET'])
@token_required
def api_list_users():
    """API: 获取用户列表 / Get user list"""
    return _paginate_query(User.query.order_by(User.created_at.desc()))


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def api_get_user(user_id):
    """API: 获取用户详情 / Get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify({'success': True, 'data': user.to_dict()})


# ==================== 日志 API ====================
@api_bp.route('/logs', methods=['GET'])
@token_required
def api_list_logs():
    """API: 获取日志列表 / Get log list"""
    return _paginate_query(LoginLog.query.order_by(LoginLog.created_at.desc()))


# ==================== 辅助函数 ====================
def _paginate_query(query):
    """分页查询辅助函数 / Pagination helper"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取模型类名
    model_class = query._entity_from_pre_ent_zero().class_
    
    return jsonify({
        'success': True,
        'data': {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    })


# ==================== 搜索 API ====================
@api_bp.route('/search', methods=['GET'])
def search():
    """全局搜索 / Global search"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({
            'success': False,
            'message': _('Search query must be at least 2 characters')
        }), 400
    
    # 搜索客户
    customers = Customer.query.filter(
        db.or_(
            Customer.company_name.contains(query),
            Customer.company_code.contains(query),
            Customer.contact_name.contains(query)
        )
    ).limit(10).all()
    
    # 搜索报表
    reports = Report.query.filter(
        Report.report_name.contains(query)
    ).limit(10).all()
    
    # 搜索用户
    users = User.query.filter(
        db.or_(
            User.username.contains(query),
            User.real_name.contains(query),
            User.email.contains(query)
        )
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': {
            'customers': [c.to_dict() for c in customers],
            'reports': [r.to_dict() for r in reports],
            'users': [u.to_dict() for u in users]
        }
    })
