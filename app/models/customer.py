"""
客户模型 / Customer Model
"""
from datetime import datetime
from . import db


class Customer(db.Model):
    """
    客户模型 - 代理记账客户
    Customer Model - Accounting service customers
    """
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 基本信息 / Basic Information
    company_name = db.Column(db.String(200), nullable=False, index=True, comment='公司名称')
    company_code = db.Column(db.String(50), unique=True, nullable=True, index=True, comment='公司编码/统一社会信用代码')
    company_type = db.Column(db.String(50), nullable=True, comment='公司类型')
    industry = db.Column(db.String(100), nullable=True, comment='所属行业')
    
    # 联系信息 / Contact Information
    contact_name = db.Column(db.String(50), nullable=True, comment='联系人姓名')
    contact_phone = db.Column(db.String(20), nullable=True, comment='联系人电话')
    contact_email = db.Column(db.String(120), nullable=True, comment='联系人邮箱')
    address = db.Column(db.String(300), nullable=True, comment='公司地址')
    
    # 税务信息 / Tax Information
    tax_id = db.Column(db.String(50), unique=True, nullable=True, comment='纳税人识别号')
    tax_type = db.Column(db.String(20), default='small_scale', comment='纳税人类型: small_scale-小规模, general-一般纳税人')
    tax_bureau = db.Column(db.String(100), nullable=True, comment='所属税务局')
    
    # 代理记账信息 / Accounting Service Information
    service_start_date = db.Column(db.Date, nullable=True, comment='服务开始日期')
    service_end_date = db.Column(db.Date, nullable=True, comment='服务结束日期')
    service_fee = db.Column(db.Numeric(10, 2), nullable=True, comment='服务费用')
    service_cycle = db.Column(db.String(20), default='monthly', comment='服务周期: monthly-月, quarterly-季, yearly-年')
    
    # 状态 / Status
    # active-正常服务, suspended-暂停, terminated-终止, pending-待开始
    status = db.Column(db.String(20), default='active', nullable=False, index=True, comment='客户状态')
    
    # 备注 / Remarks
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    
    # 用户关联 / User association (for customer login)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True, comment='关联用户ID')
    
    # 日本企业特定字段 / Japanese enterprise specific fields
    customer_code = db.Column(db.String(50), unique=True, nullable=True, index=True, comment='客户编号')
    company_name_kana = db.Column(db.String(200), nullable=True, comment='公司名称片假名')
    representative_name = db.Column(db.String(100), nullable=True, comment='代表者姓名')
    phone_number = db.Column(db.String(20), nullable=True, comment='电话号码')
    tax_number = db.Column(db.String(50), nullable=True, comment='法人番号')
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='是否激活')
    
    # 负责会计 / Assigned Accountant
    accountant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True, comment='负责会计ID')
    
    # 时间戳 / Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    # 关联关系 / Relationships
    reports = db.relationship('Report', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.company_name}>'
    
    def is_active_service(self):
        """检查服务是否处于活跃状态 / Check if service is active"""
        return self.status == 'active'
    
    def get_service_status_display(self):
        """获取服务状态显示文本 / Get service status display text"""
        status_map = {
            'active': '正常服务',
            'suspended': '暂停服务',
            'terminated': '服务终止',
            'pending': '待开始'
        }
        return status_map.get(self.status, self.status)
    
    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_code': self.company_code,
            'company_type': self.company_type,
            'industry': self.industry,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'address': self.address,
            'tax_id': self.tax_id,
            'tax_type': self.tax_type,
            'tax_bureau': self.tax_bureau,
            'service_start_date': self.service_start_date.isoformat() if self.service_start_date else None,
            'service_end_date': self.service_end_date.isoformat() if self.service_end_date else None,
            'service_fee': float(self.service_fee) if self.service_fee else None,
            'service_cycle': self.service_cycle,
            'status': self.status,
            'remarks': self.remarks,
            'accountant_id': self.accountant_id,
            'accountant_name': self.accountant.real_name if self.accountant else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_status_choices():
        """获取状态选项 / Get status choices"""
        return [
            ('active', '正常服务'),
            ('suspended', '暂停服务'),
            ('terminated', '服务终止'),
            ('pending', '待开始')
        ]
    
    @staticmethod
    def get_tax_type_choices():
        """获取纳税人类型选项 / Get tax type choices"""
        return [
            ('small_scale', '小规模纳税人'),
            ('general', '一般纳税人')
        ]
    
    @staticmethod
    def get_service_cycle_choices():
        """获取服务周期选项 / Get service cycle choices"""
        return [
            ('monthly', '按月'),
            ('quarterly', '按季'),
            ('yearly', '按年')
        ]
