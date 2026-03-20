"""
报表模型 / Report Model
"""
from datetime import datetime
from . import db


class Report(db.Model):
    """
    报表模型 - 客户财务报表和税务申报表
    Report Model - Customer financial reports and tax returns
    """
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 报表基本信息 / Report Basic Information
    report_name = db.Column(db.String(200), nullable=False, comment='报表名称')
    report_type = db.Column(db.String(50), nullable=False, index=True, comment='报表类型')
    
    # 报表类型: 
    # balance_sheet-资产负债表, income_statement-利润表, 
    # cash_flow-现金流量表, tax_return-纳税申报表,
    # general_ledger-总账, detail_ledger-明细账,
    # bank_statement-银行对账单, other-其他
    
    # 所属期间 / Reporting Period
    year = db.Column(db.Integer, nullable=False, comment='报表年份')
    month = db.Column(db.Integer, nullable=True, comment='报表月份')
    report_quarter = db.Column(db.Integer, nullable=True, comment='报表季度')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='上传日期')
    
    # 关联客户 / Associated Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True, comment='客户ID')
    
    # 文件信息 / File Information
    file_path = db.Column(db.String(500), nullable=True, comment='文件存储路径')
    file_name = db.Column(db.String(200), nullable=True, comment='原始文件名')
    file_size = db.Column(db.Integer, nullable=True, comment='文件大小(字节)')
    file_type = db.Column(db.String(50), nullable=True, comment='文件类型')
    
    # 报表状态 / Report Status
    # draft-草稿, submitted-已提交, reviewed-已审核, approved-已批准, archived-已归档
    status = db.Column(db.String(20), default='draft', nullable=False, index=True, comment='报表状态')
    
    # 审核信息 / Review Information
    submitted_at = db.Column(db.DateTime, nullable=True, comment='提交时间')
    reviewed_at = db.Column(db.DateTime, nullable=True, comment='审核时间')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='审核人ID')
    
    # 下载统计 / Download Statistics
    download_count = db.Column(db.Integer, default=0, nullable=False, comment='下载次数')
    last_downloaded_at = db.Column(db.DateTime, nullable=True, comment='最后下载时间')
    
    # 备注 / Remarks
    description = db.Column(db.Text, nullable=True, comment='报表描述')
    remarks = db.Column(db.Text, nullable=True, comment='备注')
    
    # 时间戳 / Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='创建人ID')
    
    # 关联关系 / Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_reports')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_reports')
    
    def __repr__(self):
        return f'<Report {self.report_name}>'
    
    def get_period_display(self):
        """获取期间显示文本 / Get period display text"""
        if self.month:
            return f"{self.year}年{self.month}月"
        elif self.report_quarter:
            return f"{self.year}年第{self.report_quarter}季度"
        else:
            return f"{self.year}年"
    
    def get_status_display(self):
        """获取状态显示文本 / Get status display text"""
        status_map = {
            'draft': '草稿',
            'submitted': '已提交',
            'reviewed': '已审核',
            'approved': '已批准',
            'archived': '已归档'
        }
        return status_map.get(self.status, self.status)
    
    def get_report_type_display(self):
        """获取报表类型显示文本 / Get report type display text"""
        type_map = {
            'monthly': '月报',
            'balance_sheet': '资产负债表',
            'income_statement': '利润表',
            'cash_flow': '现金流量表',
            'equity_change': '所有者权益变动表',
            'tax_return': '纳税申报表',
            'general_ledger': '总账',
            'detail_ledger': '明细账',
            'bank_statement': '银行对账单',
            'other': '其他'
        }
        return type_map.get(self.report_type, self.report_type)
    
    def submit(self):
        """提交报表 / Submit report"""
        self.status = 'submitted'
        self.submitted_at = datetime.utcnow()
    
    def review(self, reviewer_id):
        """审核报表 / Review report"""
        self.status = 'reviewed'
        self.reviewed_at = datetime.utcnow()
        self.reviewed_by = reviewer_id
    
    def approve(self):
        """批准报表 / Approve report"""
        self.status = 'approved'
    
    def archive(self):
        """归档报表 / Archive report"""
        self.status = 'archived'
    
    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'id': self.id,
            'report_name': self.report_name,
            'report_type': self.report_type,
            'report_type_display': self.get_report_type_display(),
            'year': self.year,
            'month': self.month,
            'report_quarter': self.report_quarter,
            'period_display': self.get_period_display(),
            'customer_id': self.customer_id,
            'customer_name': self.customer.company_name if self.customer else None,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status,
            'status_display': self.get_status_display(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'download_count': self.download_count,
            'last_downloaded_at': self.last_downloaded_at.isoformat() if self.last_downloaded_at else None,
            'description': self.description,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None
        }
    
    @staticmethod
    def get_type_choices():
        """获取报表类型选项 / Get report type choices"""
        return [
            ('balance_sheet', '资产负债表'),
            ('income_statement', '利润表'),
            ('cash_flow', '现金流量表'),
            ('equity_change', '所有者权益变动表'),
            ('tax_return', '纳税申报表'),
            ('general_ledger', '总账'),
            ('detail_ledger', '明细账'),
            ('bank_statement', '银行对账单'),
            ('other', '其他')
        ]
    
    @staticmethod
    def get_status_choices():
        """获取状态选项 / Get status choices"""
        return [
            ('draft', '草稿'),
            ('submitted', '已提交'),
            ('reviewed', '已审核'),
            ('approved', '已批准'),
            ('archived', '已归档')
        ]
