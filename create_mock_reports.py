"""
创建日本四大报表模拟数据
日本四大报表：
1. 貸借対照表 (Balance Sheet) - 资产负债表
2. 損益計算書 (Income Statement) - 损益表/利润表
3. キャッシュ・フロー計算書 (Cash Flow Statement) - 现金流量表
4. 株主資本等変動計算書 (Statement of Changes in Equity) - 所有者权益变动表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app import create_app
from app.models import db
from app.models.report import Report
from app.models.customer import Customer
from app.models.user import User

app = create_app()

with app.app_context():
    # 获取第一个客户
    customer = Customer.query.first()
    if not customer:
        print("错误：没有找到客户，请先创建客户")
        sys.exit(1)
    
    # 获取第一个用户作为创建者
    user = User.query.first()
    created_by = user.id if user else None
    
    print(f"为客户 {customer.company_name} (ID: {customer.id}) 创建模拟报表数据")
    
    # 定义两个月的数据（2025年1月和2月）
    months = [
        {'year': 2025, 'month': 1, 'period': '2025年1月'},
        {'year': 2025, 'month': 2, 'period': '2025年2月'}
    ]
    
    # 日本四大报表类型
    report_types = [
        {
            'type': 'balance_sheet',
            'name': '资产负债表',
            'japanese_name': '貸借対照表',
            'description': '展示资产、负债和所有者权益的财务状况'
        },
        {
            'type': 'income_statement',
            'name': '损益表',
            'japanese_name': '損益計算書',
            'description': '展示收入、成本、费用及利润情况'
        },
        {
            'type': 'cash_flow',
            'name': '现金流量表',
            'japanese_name': 'キャッシュ・フロー計算書',
            'description': '展示现金流入和流出的情况'
        },
        {
            'type': 'equity_change',
            'name': '所有者权益变动表',
            'japanese_name': '株主資本等変動計算書',
            'description': '展示股东权益的变动情况'
        }
    ]
    
    created_count = 0
    
    for month_data in months:
        for report_type in report_types:
            # 检查是否已存在
            existing = Report.query.filter_by(
                customer_id=customer.id,
                report_type=report_type['type'],
                year=month_data['year'],
                month=month_data['month']
            ).first()
            
            if existing:
                print(f"  已存在: {report_type['name']} - {month_data['period']}")
                continue
            
            # 创建报表
            report = Report(
                report_name=f"{month_data['period']}{report_type['name']}",
                report_type=report_type['type'],
                year=month_data['year'],
                month=month_data['month'],
                customer_id=customer.id,
                file_name=f"{report_type['type']}_{month_data['year']}{month_data['month']:02d}.pdf",
                file_type='application/pdf',
                file_size=1024 * 1024 * (2 + hash(report_type['type']) % 5),  # 2-6MB随机大小
                status='approved',  # 已批准状态
                description=f"{report_type['japanese_name']}\n{report_type['description']}",
                remarks=f"模拟数据 - 日本财务报表\n报表类型: {report_type['japanese_name']}",
                created_by=created_by,
                upload_date=datetime(month_data['year'], month_data['month'], 15),
                created_at=datetime(month_data['year'], month_data['month'], 10),
                updated_at=datetime(month_data['year'], month_data['month'], 15)
            )
            
            # 设置审核状态
            report.status = 'approved'
            report.submitted_at = datetime(month_data['year'], month_data['month'], 12)
            report.reviewed_at = datetime(month_data['year'], month_data['month'], 14)
            report.reviewed_by = created_by
            
            db.session.add(report)
            created_count += 1
            print(f"  创建: {report.report_name}")
    
    # 提交事务
    db.session.commit()
    print(f"\n成功创建 {created_count} 条模拟报表记录")
    
    # 显示统计
    print("\n报表统计:")
    for report_type in report_types:
        count = Report.query.filter_by(
            customer_id=customer.id,
            report_type=report_type['type']
        ).count()
        print(f"  {report_type['name']}: {count} 份")
