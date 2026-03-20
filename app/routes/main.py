"""
主页面路由 / Main Routes
"""
from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from flask_babel import gettext as _
from datetime import datetime, timedelta

from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.report import Report
from app.models.login_log import LoginLog

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页 / Home page"""
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login_page'))


@main_bp.route('/health')
def health_check():
    """健康检查接口 / Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'accounting-system'
    })


@main_bp.route('/dashboard')
def dashboard():
    """仪表盘 / Dashboard"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # 判断用户角色 - 管理员跳转到管理员仪表盘
    if user.is_admin or user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    # 获取关联的客户信息
    customer = Customer.query.filter_by(user_id=user_id).first()
    
    # 获取上次登录信息
    last_login = LoginLog.query.filter_by(user_id=user_id, success=True).order_by(LoginLog.login_time.desc()).offset(1).first()
    
    # 初始化统计数据
    total_reports = 0
    monthly_reports = 0
    balance_sheets = 0
    income_statements = 0
    detail_ledgers = 0
    this_month_reports = 0
    unread_count = 0
    recent_reports = []
    
    if customer:
        # 获取所有报表统计
        total_reports = Report.query.filter_by(customer_id=customer.id).count()
        
        # 获取各类报表数量
        monthly_reports = Report.query.filter_by(customer_id=customer.id, report_type='monthly').count()
        balance_sheets = Report.query.filter_by(customer_id=customer.id, report_type='balance_sheet').count()
        income_statements = Report.query.filter_by(customer_id=customer.id, report_type='income_statement').count()
        detail_ledgers = Report.query.filter_by(customer_id=customer.id, report_type='detail_ledger').count()
        
        # 获取本月报表数量
        now = datetime.now()
        this_month_reports = Report.query.filter_by(
            customer_id=customer.id,
            year=now.year,
            month=now.month
        ).count()
        
        # 未读报表数量（这里简化为最近3天上传的）
        three_days_ago = now - timedelta(days=3)
        unread_count = Report.query.filter(
            Report.customer_id == customer.id,
            Report.upload_date >= three_days_ago
        ).count()
        
        # 获取最近的报表
        reports = Report.query.filter_by(customer_id=customer.id).order_by(Report.upload_date.desc()).limit(5).all()
        report_type_map = {
            'monthly': '月报',
            'balance_sheet': '资产负债表',
            'income_statement': '利润表',
            'cash_flow': '现金流量表',
            'tax_return': '纳税申报表',
            'detail_ledger': '明细账',
            'general_ledger': '总账',
            'bank_statement': '银行对账单',
            'other': '其他'
        }
        for report in reports:
            recent_reports.append({
                'id': report.id,
                'file_name': report.file_name,
                'report_type_name': report_type_map.get(report.report_type, report.report_type),
                'report_period': f"{report.year}年{report.month}月",
                'upload_date': report.upload_date.strftime('%Y-%m-%d %H:%M')
            })
    
    return render_template('customer/dashboard.html',
                           user=user,
                           customer=customer,
                           last_login=last_login,
                           recent_reports=recent_reports,
                           total_reports=total_reports,
                           monthly_reports=monthly_reports,
                           balance_sheets=balance_sheets,
                           income_statements=income_statements,
                           detail_ledgers=detail_ledgers,
                           this_month_reports=this_month_reports,
                           unread_count=unread_count)
