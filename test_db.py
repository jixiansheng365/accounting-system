"""
简单测试数据库初始化
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试数据库初始化...")

try:
    from app import create_app
    from app.models import db
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.report import Report
    from app.models.login_log import LoginLog
    from datetime import datetime, timedelta
    
    print("✓ 导入模块成功")
    
    app = create_app('development')
    print("✓ 创建应用成功")
    
    with app.app_context():
        # 删除旧表
        db.drop_all()
        print("✓ 删除旧表成功")
        
        # 创建新表
        db.create_all()
        print("✓ 创建新表成功")
        
        # 创建测试用户
        test_user = User(
            username='CUST001',
            email='cust001@example.com',
            real_name='山田 太郎',
            role='customer'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        print("✓ 创建测试用户成功")
        
        # 创建测试客户
        test_customer = Customer(
            user_id=1,
            customer_code='CUST001',
            company_name='株式会社サンプル',
            company_name_kana='カブシキガイシャサンプル',
            representative_name='山田 太郎',
            phone_number='03-1234-5678',
            contact_email='info@sample.co.jp',
            address='東京都千代田区1-1-1',
            tax_number='1234567890123',
            industry='製造業',
            is_active=True
        )
        db.session.add(test_customer)
        print("✓ 创建测试客户成功")
        
        # 创建报表类型
        report_types = ['monthly', 'balance_sheet', 'income_statement']
        report_type_names = {
            'monthly': '月次報告書',
            'balance_sheet': '貸借対照表',
            'income_statement': '損益計算書'
        }
        
        now = datetime.now()
        for i in range(3):
            report_date = now - timedelta(days=30 * i)
            for report_type in report_types:
                report = Report(
                    customer_id=1,
                    report_name=f"{report_type_names[report_type]}_{report_date.year}年{report_date.month}月",
                    report_type=report_type,
                    year=report_date.year,
                    month=report_date.month,
                    file_name=f"{report_type_names[report_type]}_{report_date.year}年{report_date.month}月.pdf",
                    file_path=f"/uploads/{report_type}_{report_date.year}{report_date.month:02d}.pdf",
                    file_size=102400 + i * 1024,
                    upload_date=report_date
                )
                db.session.add(report)
        print("✓ 创建测试报表成功")
        
        # 创建登录日志
        for i in range(5):
            login_time = now - timedelta(hours=2 * i)
            login_log = LoginLog(
                user_id=1,
                username='CUST001',
                action='login',
                ip_address=f'192.168.1.{100 + i}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                login_time=login_time,
                success=True,
                location='東京都'
            )
            db.session.add(login_log)
        print("✓ 创建登录日志成功")
        
        db.session.commit()
        print("✓ 提交数据成功")
        
        print("\n" + "="*50)
        print("测试账号信息:")
        print("  客户编号: CUST001")
        print("  密码: password123")
        print("="*50)
        print("\n数据库初始化成功！")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
