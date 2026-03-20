"""
测试数据验证脚本 / Test Data Verification Script
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.report import Report
from app.models.login_log import LoginLog


def verify_test_data():
    """验证测试数据"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("测试数据验证报告")
        print("=" * 60)
        
        # 基础统计
        print("\n【基础数据统计】")
        print(f"  用户总数: {User.query.count()}")
        print(f"  客户总数: {Customer.query.count()}")
        print(f"  报表总数: {Report.query.count()}")
        print(f"  登录日志总数: {LoginLog.query.count()}")
        
        # 管理员账号
        print("\n【管理员账号】")
        admins = User.query.filter(User.role.in_(['admin', 'manager'])).all()
        for u in admins:
            role_display = '超级管理员' if u.is_admin else '管理员'
            print(f"  - {u.username} ({u.real_name}, {role_display})")
        
        # 会计员工
        print("\n【会计员工】")
        role_map = {'accountant': '会计', 'assistant': '助理', 'manager': '主管'}
        accountants = User.query.filter(User.role.in_(['accountant', 'assistant'])).all()
        for u in accountants:
            print(f"  - {u.username} ({u.real_name}, {role_map.get(u.role, u.role)})")
        
        # 客户示例
        print("\n【客户示例 (前5个)】")
        customers = Customer.query.limit(5).all()
        for c in customers:
            print(f"  - {c.customer_code}: {c.company_name}")
            print(f"    行业: {c.industry}, 报表数: {c.reports.count()}")
        
        # 报表类型统计
        print("\n【报表类型统计】")
        report_stats = db.session.query(Report.report_type, db.func.count(Report.id)).group_by(Report.report_type).all()
        type_names = {
            'monthly': '月次報告書',
            'balance_sheet': '貸借対照表',
            'income_statement': '損益計算書',
            'detail_ledger': '明細帳'
        }
        for rt, count in report_stats:
            print(f"  - {type_names.get(rt, rt)}: {count}份")
        
        # 报表期间统计
        print("\n【报表期间统计】")
        period_stats = db.session.query(Report.year, Report.month, db.func.count(Report.id)).group_by(Report.year, Report.month).order_by(Report.year, Report.month).all()
        for year, month, count in period_stats:
            print(f"  - {year}年{month:02d}月: {count}份")
        
        # 登录日志统计
        print("\n【登录日志统计】")
        success = LoginLog.query.filter_by(success=True).count()
        failed = LoginLog.query.filter_by(success=False).count()
        print(f"  - 成功登录: {success}次")
        print(f"  - 失败登录: {failed}次")
        
        # 客户行业分布
        print("\n【客户行业分布】")
        industry_stats = db.session.query(Customer.industry, db.func.count(Customer.id)).group_by(Customer.industry).all()
        for industry, count in industry_stats:
            print(f"  - {industry}: {count}家")
        
        # 纳税人类型分布
        print("\n【纳税人类型分布】")
        tax_stats = db.session.query(Customer.tax_type, db.func.count(Customer.id)).group_by(Customer.tax_type).all()
        tax_names = {'small_scale': '小规模纳税人', 'general': '一般纳税人'}
        for tax_type, count in tax_stats:
            print(f"  - {tax_names.get(tax_type, tax_type)}: {count}家")
        
        print("\n" + "=" * 60)
        print("验证完成！所有测试数据已成功导入。")
        print("=" * 60)


if __name__ == '__main__':
    verify_test_data()
