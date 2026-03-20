"""
客户服务层 / Customer Service Layer
处理客户相关的业务逻辑
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from flask_babel import gettext as _

from app.models import db
from app.models.customer import Customer
from app.models.user import User
from app.models.report import Report


class CustomerService:
    """客户服务类 / Customer Service Class"""
    
    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        """
        根据ID获取客户 / Get customer by ID
        
        Args:
            customer_id: 客户ID
            
        Returns:
            Customer对象或None
        """
        return Customer.query.get(customer_id)
    
    @staticmethod
    def get_customer_by_company_name(company_name: str) -> Optional[Customer]:
        """
        根据公司名称获取客户 / Get customer by company name
        
        Args:
            company_name: 公司名称
            
        Returns:
            Customer对象或None
        """
        return Customer.query.filter_by(company_name=company_name).first()
    
    @staticmethod
    def get_customer_by_company_code(company_code: str) -> Optional[Customer]:
        """
        根据公司编码获取客户 / Get customer by company code
        
        Args:
            company_code: 公司编码/统一社会信用代码
            
        Returns:
            Customer对象或None
        """
        return Customer.query.filter_by(company_code=company_code).first()
    
    @staticmethod
    def get_customer_by_user_id(user_id: int) -> Optional[Customer]:
        """
        根据用户ID获取客户 / Get customer by user ID
        
        Args:
            user_id: 用户ID
            
        Returns:
            Customer对象或None
        """
        return Customer.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def list_customers(
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        accountant_id: Optional[int] = None,
        search: Optional[str] = None,
        tax_type: Optional[str] = None,
        order_by: str = 'created_at',
        order_desc: bool = True
    ) -> Tuple[List[Customer], int]:
        """
        获取客户列表 / Get customer list
        
        Args:
            page: 页码
            per_page: 每页数量
            status: 状态筛选
            accountant_id: 负责会计ID筛选
            search: 搜索关键词
            tax_type: 纳税人类型筛选
            order_by: 排序字段
            order_desc: 是否降序
            
        Returns:
            (客户列表, 总数)
        """
        query = Customer.query
        
        # 应用筛选条件
        if status:
            query = query.filter_by(status=status)
        
        if accountant_id:
            query = query.filter_by(accountant_id=accountant_id)
        
        if tax_type:
            query = query.filter_by(tax_type=tax_type)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Customer.company_name.contains(search),
                    Customer.company_code.contains(search),
                    Customer.contact_name.contains(search),
                    Customer.contact_phone.contains(search),
                    Customer.tax_id.contains(search)
                )
            )
        
        # 应用排序
        order_column = getattr(Customer, order_by, Customer.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def create_customer(data: Dict[str, Any]) -> Tuple[Customer, Optional[str]]:
        """
        创建客户 / Create customer
        
        Args:
            data: 客户数据字典
            
        Returns:
            (Customer对象, 错误信息)
        """
        # 验证必填字段
        if not data.get('company_name'):
            return None, _('Company name is required')
        
        # 检查公司名称是否已存在
        if Customer.query.filter_by(company_name=data['company_name']).first():
            return None, _('Company name already exists')
        
        # 检查公司编码是否已存在
        if data.get('company_code') and Customer.query.filter_by(company_code=data['company_code']).first():
            return None, _('Company code already exists')
        
        # 检查统一社会信用代码是否已存在
        if data.get('tax_id') and Customer.query.filter_by(tax_id=data['tax_id']).first():
            return None, _('Tax ID already exists')
        
        try:
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
                accountant_id=data.get('accountant_id'),
                user_id=data.get('user_id'),
                customer_code=data.get('customer_code'),
                company_name_kana=data.get('company_name_kana'),
                representative_name=data.get('representative_name'),
                phone_number=data.get('phone_number'),
                tax_number=data.get('tax_number'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(customer)
            db.session.commit()
            
            return customer, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_customer(customer_id: int, data: Dict[str, Any]) -> Tuple[Optional[Customer], Optional[str]]:
        """
        更新客户信息 / Update customer
        
        Args:
            customer_id: 客户ID
            data: 更新数据字典
            
        Returns:
            (Customer对象, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return None, _('Customer not found')
        
        # 检查公司名称唯一性（如果更改了名称）
        if data.get('company_name') and data['company_name'] != customer.company_name:
            if Customer.query.filter_by(company_name=data['company_name']).first():
                return None, _('Company name already exists')
        
        # 检查公司编码唯一性
        if data.get('company_code') and data['company_code'] != customer.company_code:
            if Customer.query.filter_by(company_code=data['company_code']).first():
                return None, _('Company code already exists')
        
        # 检查税号唯一性
        if data.get('tax_id') and data['tax_id'] != customer.tax_id:
            if Customer.query.filter_by(tax_id=data['tax_id']).first():
                return None, _('Tax ID already exists')
        
        try:
            # 可更新的字段
            fields = [
                'company_name', 'company_code', 'company_type', 'industry',
                'contact_name', 'contact_phone', 'contact_email', 'address',
                'tax_id', 'tax_type', 'tax_bureau', 'service_start_date',
                'service_end_date', 'service_fee', 'service_cycle', 'status',
                'remarks', 'accountant_id', 'user_id',
                'customer_code', 'company_name_kana', 'representative_name',
                'phone_number', 'tax_number', 'is_active'
            ]
            
            for field in fields:
                if field in data:
                    setattr(customer, field, data[field])
            
            db.session.commit()
            
            return customer, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_customer(customer_id: int) -> Tuple[bool, Optional[str]]:
        """
        删除客户 / Delete customer
        
        Args:
            customer_id: 客户ID
            
        Returns:
            (是否成功, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return False, _('Customer not found')
        
        try:
            db.session.delete(customer)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def update_customer_status(customer_id: int, status: str) -> Tuple[Optional[Customer], Optional[str]]:
        """
        更新客户状态 / Update customer status
        
        Args:
            customer_id: 客户ID
            status: 新状态
            
        Returns:
            (Customer对象, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return None, _('Customer not found')
        
        valid_statuses = ['active', 'suspended', 'terminated', 'pending']
        if status not in valid_statuses:
            return None, _('Invalid status')
        
        try:
            customer.status = status
            db.session.commit()
            return customer, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def assign_accountant(customer_id: int, accountant_id: int) -> Tuple[Optional[Customer], Optional[str]]:
        """
        分配负责会计 / Assign accountant to customer
        
        Args:
            customer_id: 客户ID
            accountant_id: 会计用户ID
            
        Returns:
            (Customer对象, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return None, _('Customer not found')
        
        # 验证会计用户是否存在
        accountant = User.query.get(accountant_id)
        if not accountant:
            return None, _('Accountant not found')
        
        if not accountant.is_active:
            return None, _('Accountant account is disabled')
        
        try:
            customer.accountant_id = accountant_id
            db.session.commit()
            return customer, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def reset_customer_password(customer_id: int, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        重置客户登录密码 / Reset customer password
        
        Args:
            customer_id: 客户ID
            new_password: 新密码
            
        Returns:
            (是否成功, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return False, _('Customer not found')
        
        if not customer.user_id:
            return False, _('Customer does not have a login account')
        
        user = User.query.get(customer.user_id)
        if not user:
            return False, _('Customer user account not found')
        
        try:
            user.set_password(new_password)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def create_customer_login_account(customer_id: int, username: str, password: str, email: str = None) -> Tuple[Optional[User], Optional[str]]:
        """
        为客户创建登录账号 / Create login account for customer
        
        Args:
            customer_id: 客户ID
            username: 用户名
            password: 密码
            email: 邮箱
            
        Returns:
            (User对象, 错误信息)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return None, _('Customer not found')
        
        # 检查客户是否已有账号
        if customer.user_id:
            return None, _('Customer already has a login account')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return None, _('Username already exists')
        
        # 检查邮箱是否已存在
        if email and User.query.filter_by(email=email).first():
            return None, _('Email already exists')
        
        try:
            # 创建客户用户账号
            user = User(
                username=username,
                email=email or f'{username}@customer.local',
                real_name=customer.contact_name or customer.company_name,
                phone=customer.contact_phone,
                role='customer',  # 客户角色
                is_active=True,
                is_admin=False
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # 获取user.id
            
            # 关联客户和用户
            customer.user_id = user.id
            
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_customer_statistics() -> Dict[str, Any]:
        """
        获取客户统计信息 / Get customer statistics
        
        Returns:
            统计信息字典
        """
        total = Customer.query.count()
        active = Customer.query.filter_by(status='active').count()
        suspended = Customer.query.filter_by(status='suspended').count()
        pending = Customer.query.filter_by(status='pending').count()
        terminated = Customer.query.filter_by(status='terminated').count()
        
        # 按纳税人类型统计
        small_scale = Customer.query.filter_by(tax_type='small_scale').count()
        general = Customer.query.filter_by(tax_type='general').count()
        
        # 按服务周期统计
        monthly = Customer.query.filter_by(service_cycle='monthly').count()
        quarterly = Customer.query.filter_by(service_cycle='quarterly').count()
        yearly = Customer.query.filter_by(service_cycle='yearly').count()
        
        # 本月新增客户
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = Customer.query.filter(Customer.created_at >= current_month).count()
        
        return {
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
            },
            'by_service_cycle': {
                'monthly': monthly,
                'quarterly': quarterly,
                'yearly': yearly
            },
            'new_this_month': new_this_month
        }
    
    @staticmethod
    def get_customer_reports(customer_id: int, page: int = 1, per_page: int = 20) -> Tuple[List[Report], int]:
        """
        获取客户的报表列表 / Get customer's reports
        
        Args:
            customer_id: 客户ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            (报表列表, 总数)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return [], 0
        
        pagination = Report.query.filter_by(customer_id=customer_id).order_by(
            Report.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def search_customers(
        query: str,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Customer], int]:
        """
        搜索客户 / Search customers
        
        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            (客户列表, 总数)
        """
        search_pattern = f'%{query}%'
        
        db_query = Customer.query.filter(
            db.or_(
                Customer.company_name.contains(query),
                Customer.company_code.contains(query),
                Customer.contact_name.contains(query),
                Customer.contact_phone.contains(query),
                Customer.contact_email.contains(query),
                Customer.tax_id.contains(query),
                Customer.customer_code.contains(query)
            )
        )
        
        pagination = db_query.order_by(Customer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return pagination.items, pagination.total
