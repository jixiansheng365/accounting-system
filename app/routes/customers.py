"""
客户管理路由 / Customer Management Routes
"""
from flask import Blueprint, request, jsonify
from flask_babel import gettext as _

from app.models import db
from app.models.customer import Customer
from app.models.user import User

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/', methods=['GET'])
def list_customers():
    """获取客户列表 / Get customer list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 筛选参数
    status = request.args.get('status')
    accountant_id = request.args.get('accountant_id', type=int)
    search = request.args.get('search')
    
    query = Customer.query
    
    if status:
        query = query.filter_by(status=status)
    
    if accountant_id:
        query = query.filter_by(accountant_id=accountant_id)
    
    if search:
        query = query.filter(
            db.or_(
                Customer.company_name.contains(search),
                Customer.company_code.contains(search),
                Customer.contact_name.contains(search)
            )
        )
    
    pagination = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'items': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    })


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """获取客户详情 / Get customer details"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'success': True,
        'data': customer.to_dict()
    })


@customers_bp.route('/', methods=['POST'])
def create_customer():
    """创建客户 / Create customer"""
    data = request.get_json() or {}
    
    # 必填字段验证
    if not data.get('company_name'):
        return jsonify({
            'success': False,
            'message': _('Company name is required')
        }), 400
    
    # 检查公司名是否已存在
    if Customer.query.filter_by(company_name=data['company_name']).first():
        return jsonify({
            'success': False,
            'message': _('Company name already exists')
        }), 400
    
    customer = Customer(
        company_name=data.get('company_name'),
        company_code=data.get('company_code'),
        company_type=data.get('company_type'),
        industry=data.get('industry'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
        contact_email=data.get('contact_email'),
        address=data.get('address'),
        tax_id=data.get('tax_id'),
        tax_type=data.get('tax_type', 'small_scale'),
        tax_bureau=data.get('tax_bureau'),
        service_start_date=data.get('service_start_date'),
        service_end_date=data.get('service_end_date'),
        service_fee=data.get('service_fee'),
        service_cycle=data.get('service_cycle', 'monthly'),
        status=data.get('status', 'active'),
        remarks=data.get('remarks'),
        accountant_id=data.get('accountant_id')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Customer created successfully'),
        'data': customer.to_dict()
    }), 201


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客户信息 / Update customer"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}
    
    # 更新字段
    fields = [
        'company_name', 'company_code', 'company_type', 'industry',
        'contact_name', 'contact_phone', 'contact_email', 'address',
        'tax_id', 'tax_type', 'tax_bureau', 'service_start_date',
        'service_end_date', 'service_fee', 'service_cycle', 'status',
        'remarks', 'accountant_id'
    ]
    
    for field in fields:
        if field in data:
            setattr(customer, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Customer updated successfully'),
        'data': customer.to_dict()
    })


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """删除客户 / Delete customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Customer deleted successfully')
    })


@customers_bp.route('/<int:customer_id>/status', methods=['PATCH'])
def update_customer_status(customer_id):
    """更新客户状态 / Update customer status"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}
    
    new_status = data.get('status')
    if not new_status:
        return jsonify({
            'success': False,
            'message': _('Status is required')
        }), 400
    
    valid_statuses = ['active', 'suspended', 'terminated', 'pending']
    if new_status not in valid_statuses:
        return jsonify({
            'success': False,
            'message': _('Invalid status')
        }), 400
    
    customer.status = new_status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Status updated successfully'),
        'data': customer.to_dict()
    })


@customers_bp.route('/statistics', methods=['GET'])
def get_customer_statistics():
    """获取客户统计信息 / Get customer statistics"""
    total = Customer.query.count()
    active = Customer.query.filter_by(status='active').count()
    suspended = Customer.query.filter_by(status='suspended').count()
    pending = Customer.query.filter_by(status='pending').count()
    terminated = Customer.query.filter_by(status='terminated').count()
    
    # 按纳税人类型统计
    small_scale = Customer.query.filter_by(tax_type='small_scale').count()
    general = Customer.query.filter_by(tax_type='general').count()
    
    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'by_status': {
                'active': active,
                'suspended': suspended,
                'pending': pending,
                'terminated': terminated
            },
            'by_tax_type': {
                'small_scale': small_scale,
                'general': general
            }
        }
    })
