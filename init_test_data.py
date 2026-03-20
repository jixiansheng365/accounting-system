"""
测试数据初始化脚本 / Test Data Initialization Script
为代理记账客户管理系统创建完整的测试数据
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User
from app.models.customer import Customer
from app.models.report import Report
from app.models.login_log import LoginLog


# ============ 测试数据配置 ============
DEFAULT_PASSWORD = 'Test@123456'  # 统一测试密码

# 管理员账号数据
ADMIN_USERS = [
    {'username': 'admin', 'email': 'admin@accounting.jp', 'real_name': 'システム管理者', 'role': 'admin'},
    {'username': 'admin2', 'email': 'admin2@accounting.jp', 'real_name': '副管理者', 'role': 'admin'},
    {'username': 'manager1', 'email': 'manager@accounting.jp', 'real_name': '営業部長', 'role': 'manager'},
]

# 会计员工数据
ACCOUNTANT_USERS = [
    {'username': 'accountant1', 'email': 'acct1@accounting.jp', 'real_name': '田中 健一', 'role': 'accountant'},
    {'username': 'accountant2', 'email': 'acct2@accounting.jp', 'real_name': '佐藤 美咲', 'role': 'accountant'},
    {'username': 'assistant1', 'email': 'asst1@accounting.jp', 'real_name': '鈴木 太郎', 'role': 'assistant'},
]

# 日本企业客户数据
CUSTOMERS_DATA = [
    # 制造业 (3家)
    {
        'customer_code': 'CUST001',
        'company_name': '株式会社東京精密製作所',
        'company_name_kana': 'カブシキガイシャトウキョウセイミクセイサクショ',
        'representative_name': '山田 太郎',
        'industry': '製造業',
        'company_type': '株式会社',
        'phone_number': '03-1234-5678',
        'contact_email': 'info@tokyo-seimitsu.co.jp',
        'address': '東京都大田区南蒲田1-1-1',
        'tax_number': '1234567890123',
        'tax_id': 'T12345678901',
        'tax_type': 'general',
        'tax_bureau': '東京国税局',
        'service_start_date': '2023-04-01',
        'service_fee': 150000,
    },
    {
        'customer_code': 'CUST002',
        'company_name': '大阪金属工業株式会社',
        'company_name_kana': 'オオサカキンゾクコウギョウカブシキガイシャ',
        'representative_name': '田中 一郎',
        'industry': '製造業',
        'company_type': '株式会社',
        'phone_number': '06-2345-6789',
        'contact_email': 'contact@osaka-metal.co.jp',
        'address': '大阪府大阪市中央区本町2-2-2',
        'tax_number': '2345678901234',
        'tax_id': 'T23456789012',
        'tax_type': 'general',
        'tax_bureau': '大阪国税局',
        'service_start_date': '2023-06-01',
        'service_fee': 120000,
    },
    {
        'customer_code': 'CUST003',
        'company_name': '名古屋自動車部品株式会社',
        'company_name_kana': 'ナゴヤジドウシャブヒンカブシキガイシャ',
        'representative_name': '佐藤 次郎',
        'industry': '製造業',
        'company_type': '株式会社',
        'phone_number': '052-3456-7890',
        'contact_email': 'sales@nagoya-auto.co.jp',
        'address': '愛知県名古屋市中区栄3-3-3',
        'tax_number': '3456789012345',
        'tax_id': 'T34567890123',
        'tax_type': 'small_scale',
        'tax_bureau': '名古屋国税局',
        'service_start_date': '2024-01-01',
        'service_fee': 80000,
    },
    # 贸易公司 (3家)
    {
        'customer_code': 'CUST004',
        'company_name': '株式会社日本貿易商事',
        'company_name_kana': 'カブシキガイシャニホンボウエキショウジ',
        'representative_name': '鈴木 三郎',
        'industry': '卸売業・小売業',
        'company_type': '株式会社',
        'phone_number': '03-4567-8901',
        'contact_email': 'trade@nippon-boeki.co.jp',
        'address': '東京都港区港南4-4-4',
        'tax_number': '4567890123456',
        'tax_id': 'T45678901234',
        'tax_type': 'general',
        'tax_bureau': '東京国税局',
        'service_start_date': '2023-08-01',
        'service_fee': 100000,
    },
    {
        'customer_code': 'CUST005',
        'company_name': '横浜国際貿易株式会社',
        'company_name_kana': 'ヨコハマコクサイボウエキカブシキガイシャ',
        'representative_name': '高橋 四郎',
        'industry': '卸売業・小売業',
        'company_type': '株式会社',
        'phone_number': '045-5678-9012',
        'contact_email': 'info@yokohama-trade.co.jp',
        'address': '神奈川県横浜市中区日本大通5-5-5',
        'tax_number': '5678901234567',
        'tax_id': 'T56789012345',
        'tax_type': 'general',
        'tax_bureau': '関東信越国税局',
        'service_start_date': '2023-10-01',
        'service_fee': 90000,
    },
    {
        'customer_code': 'CUST006',
        'company_name': '福岡輸出入株式会社',
        'company_name_kana': 'フクオカユシュツニュウカブシキガイシャ',
        'representative_name': '伊藤 五郎',
        'industry': '卸売業・小売業',
        'company_type': '株式会社',
        'phone_number': '092-6789-0123',
        'contact_email': 'export@fukuoka-trade.co.jp',
        'address': '福岡県福岡市博多区博多駅前6-6-6',
        'tax_number': '6789012345678',
        'tax_id': 'T67890123456',
        'tax_type': 'small_scale',
        'tax_bureau': '福岡国税局',
        'service_start_date': '2024-02-01',
        'service_fee': 70000,
    },
    # IT服务公司 (2家)
    {
        'customer_code': 'CUST007',
        'company_name': '株式会社テックイノベーション',
        'company_name_kana': 'カブシキガイシャテックイノベーション',
        'representative_name': '渡辺 六郎',
        'industry': '情報通信業',
        'company_type': '株式会社',
        'phone_number': '03-7890-1234',
        'contact_email': 'contact@tech-innovation.co.jp',
        'address': '東京都渋谷区渋谷7-7-7',
        'tax_number': '7890123456789',
        'tax_id': 'T78901234567',
        'tax_type': 'general',
        'tax_bureau': '東京国税局',
        'service_start_date': '2023-05-01',
        'service_fee': 110000,
    },
    {
        'customer_code': 'CUST008',
        'company_name': 'デジタルソリューションズ株式会社',
        'company_name_kana': 'デジタルソリューションズカブシキガイシャ',
        'representative_name': '木村 七郎',
        'industry': '情報通信業',
        'company_type': '株式会社',
        'phone_number': '03-8901-2345',
        'contact_email': 'info@digital-sol.co.jp',
        'address': '東京都新宿区西新宿8-8-8',
        'tax_number': '8901234567890',
        'tax_id': 'T89012345678',
        'tax_type': 'small_scale',
        'tax_bureau': '東京国税局',
        'service_start_date': '2024-03-01',
        'service_fee': 75000,
    },
    # 餐饮服务业 (2家)
    {
        'customer_code': 'CUST009',
        'company_name': '株式会社グルメダイニング',
        'company_name_kana': 'カブシキガイシャグルメダイニング',
        'representative_name': '林 八郎',
        'industry': '飲食店',
        'company_type': '株式会社',
        'phone_number': '03-9012-3456',
        'contact_email': 'info@gourmet-dining.co.jp',
        'address': '東京都中央区銀座9-9-9',
        'tax_number': '9012345678901',
        'tax_id': 'T90123456789',
        'tax_type': 'small_scale',
        'tax_bureau': '東京国税局',
        'service_start_date': '2023-07-01',
        'service_fee': 60000,
    },
    {
        'customer_code': 'CUST010',
        'company_name': '京都和食料理株式会社',
        'company_name_kana': 'キョウトワショクリョウリカブシキガイシャ',
        'representative_name': '清水 九郎',
        'industry': '飲食店',
        'company_type': '株式会社',
        'phone_number': '075-0123-4567',
        'contact_email': 'reserve@kyoto-washoku.co.jp',
        'address': '京都府京都市東山区祇園10-10-10',
        'tax_number': '0123456789012',
        'tax_id': 'T01234567890',
        'tax_type': 'small_scale',
        'tax_bureau': '大阪国税局',
        'service_start_date': '2024-04-01',
        'service_fee': 55000,
    },
    # 零售业 (2家)
    {
        'customer_code': 'CUST011',
        'company_name': '株式会社ライフストア',
        'company_name_kana': 'カブシキガイシャライフストア',
        'representative_name': '山本 十郎',
        'industry': '卸売業・小売業',
        'company_type': '株式会社',
        'phone_number': '03-1122-3344',
        'contact_email': 'shop@lifestore.co.jp',
        'address': '東京都世田谷区池尻11-11-11',
        'tax_number': '1122334455667',
        'tax_id': 'T11223344556',
        'tax_type': 'general',
        'tax_bureau': '東京国税局',
        'service_start_date': '2023-09-01',
        'service_fee': 95000,
    },
    {
        'customer_code': 'CUST012',
        'company_name': '北海道スーパーマーケット株式会社',
        'company_name_kana': 'ホッカイドウスーパーマーケットカブシキガイシャ',
        'representative_name': '佐々木 十一郎',
        'industry': '卸売業・小売業',
        'company_type': '株式会社',
        'phone_number': '011-2233-4455',
        'contact_email': 'support@hokkaido-super.co.jp',
        'address': '北海道札幌市中央区大通12-12-12',
        'tax_number': '2233445566778',
        'tax_id': 'T22334455667',
        'tax_type': 'general',
        'tax_bureau': '札幌国税局',
        'service_start_date': '2023-11-01',
        'service_fee': 130000,
    },
]

# 报表类型配置
REPORT_TYPES = [
    ('monthly', '月次報告書'),
    ('balance_sheet', '貸借対照表'),
    ('income_statement', '損益計算書'),
    ('detail_ledger', '明細帳'),
]

# 报表期间配置 (2024年10月 - 2025年3月)
REPORT_PERIODS = [
    (2024, 10), (2024, 11), (2024, 12),
    (2025, 1), (2025, 2), (2025, 3),
]

# 用户代理字符串列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

# 地理位置列表
LOCATIONS = [
    '東京都', '大阪府', '愛知県', '神奈川県', '福岡県',
    '北海道', '京都府', '兵庫県', '広島県', '宮城県',
]


def create_admin_users():
    """创建管理员账号"""
    users = []
    for admin_data in ADMIN_USERS:
        user = User(
            username=admin_data['username'],
            email=admin_data['email'],
            real_name=admin_data['real_name'],
            role=admin_data['role'],
            is_active=True,
            is_admin=(admin_data['role'] == 'admin'),
        )
        user.set_password(DEFAULT_PASSWORD)
        db.session.add(user)
        users.append(user)
    return users


def create_accountant_users():
    """创建会计员工账号"""
    users = []
    for acct_data in ACCOUNTANT_USERS:
        user = User(
            username=acct_data['username'],
            email=acct_data['email'],
            real_name=acct_data['real_name'],
            role=acct_data['role'],
            is_active=True,
            is_admin=False,
        )
        user.set_password(DEFAULT_PASSWORD)
        db.session.add(user)
        users.append(user)
    return users


def create_customer_users():
    """为客户创建登录账号"""
    users = []
    for customer_data in CUSTOMERS_DATA:
        user = User(
            username=customer_data['customer_code'],
            email=customer_data['contact_email'],
            real_name=customer_data['representative_name'],
            role='customer',
            is_active=True,
            is_admin=False,
        )
        user.set_password(DEFAULT_PASSWORD)
        db.session.add(user)
        users.append(user)
    return users


def create_customers(customer_users, accountants):
    """创建客户数据"""
    customers = []
    for i, customer_data in enumerate(CUSTOMERS_DATA):
        # 分配会计
        accountant = accountants[i % len(accountants)] if accountants else None
        
        customer = Customer(
            user_id=customer_users[i].id,
            customer_code=customer_data['customer_code'],
            company_name=customer_data['company_name'],
            company_name_kana=customer_data['company_name_kana'],
            representative_name=customer_data['representative_name'],
            industry=customer_data['industry'],
            company_type=customer_data['company_type'],
            phone_number=customer_data['phone_number'],
            contact_email=customer_data['contact_email'],
            address=customer_data['address'],
            tax_number=customer_data['tax_number'],
            tax_id=customer_data['tax_id'],
            tax_type=customer_data['tax_type'],
            tax_bureau=customer_data['tax_bureau'],
            service_start_date=datetime.strptime(customer_data['service_start_date'], '%Y-%m-%d').date(),
            service_fee=customer_data['service_fee'],
            service_cycle='monthly',
            status='active',
            is_active=True,
            accountant_id=accountant.id if accountant else None,
            contact_name=customer_data['representative_name'],
            contact_phone=customer_data['phone_number'],
        )
        db.session.add(customer)
        customers.append(customer)
    return customers


def create_reports(customers, admin_users):
    """创建报表数据"""
    reports = []
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'reports')
    os.makedirs(uploads_dir, exist_ok=True)
    
    for customer in customers:
        for year, month in REPORT_PERIODS:
            for report_type, report_name_prefix in REPORT_TYPES:
                # 生成文件名
                file_name = f"{report_name_prefix}_{customer.customer_code}_{year}年{month:02d}月.pdf"
                file_path = f"/uploads/reports/{file_name}"
                
                # 创建报表记录
                report = Report(
                    customer_id=customer.id,
                    report_name=f"{report_name_prefix} ({year}年{month}月)",
                    report_type=report_type,
                    year=year,
                    month=month,
                    file_name=file_name,
                    file_path=file_path,
                    file_size=random.randint(50000, 500000),  # 50KB - 500KB
                    file_type='application/pdf',
                    status=random.choice(['draft', 'submitted', 'reviewed', 'approved']),
                    description=f'{customer.company_name}の{report_name_prefix}です。',
                    created_by=random.choice(admin_users).id if admin_users else None,
                )
                
                # 根据状态设置时间
                if report.status in ['submitted', 'reviewed', 'approved']:
                    report.submitted_at = datetime(year, month, random.randint(1, 28))
                if report.status in ['reviewed', 'approved']:
                    report.reviewed_at = datetime(year, month, random.randint(1, 28))
                    report.reviewed_by = random.choice(admin_users).id if admin_users else None
                
                db.session.add(report)
                reports.append(report)
                
                # 创建空的PDF文件
                pdf_path = os.path.join(uploads_dir, file_name)
                if not os.path.exists(pdf_path):
                    with open(pdf_path, 'wb') as f:
                        # 写入最小的PDF文件头
                        f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000015 00000 n \n0000000066 00000 n \ntrailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n115\n%%EOF\n')
    
    return reports


def create_login_logs(customer_users):
    """创建登录日志数据"""
    logs = []
    now = datetime.now()
    
    for user in customer_users:
        # 为每个用户生成5-10条登录记录
        num_logs = random.randint(5, 10)
        for i in range(num_logs):
            login_time = now - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 90%成功率
            success = random.random() < 0.9
            
            log = LoginLog(
                user_id=user.id,
                username=user.username,
                action='login' if success else 'login_failed',
                ip_address=f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}',
                user_agent=random.choice(USER_AGENTS),
                device_type=random.choice(['desktop', 'mobile', 'tablet']),
                browser=random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                os=random.choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android']),
                success=success,
                fail_reason='パスワードが間違っています' if not success else None,
                location=random.choice(LOCATIONS),
                login_time=login_time,
            )
            db.session.add(log)
            logs.append(log)
            
            # 添加对应的登出记录（如果是成功登录）
            if success and random.random() < 0.7:  # 70%的登录有登出记录
                logout_time = login_time + timedelta(
                    minutes=random.randint(5, 120)
                )
                logout_log = LoginLog(
                    user_id=user.id,
                    username=user.username,
                    action='logout',
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    device_type=log.device_type,
                    browser=log.browser,
                    os=log.os,
                    success=True,
                    location=log.location,
                    login_time=logout_time,
                )
                db.session.add(logout_log)
                logs.append(logout_log)
    
    return logs


def generate_test_account_document(admin_users, accountant_users, customer_users, customers):
    """生成测试账号清单文档"""
    doc_content = """# 代理记账客户管理系统 - 测试账号清单

## 系统信息
- 系统名称: 代理记账客户管理系统
- 测试日期: {date}
- 统一测试密码: {password}

---

## 一、管理员账号

| 序号 | 用户名 | 邮箱 | 姓名 | 角色 | 状态 |
|------|--------|------|------|------|------|
""".format(date=datetime.now().strftime('%Y-%m-%d'), password=DEFAULT_PASSWORD)
    
    for i, user in enumerate(admin_users, 1):
        role_display = '超级管理员' if user.is_admin else '管理员'
        doc_content += f"| {i} | {user.username} | {user.email} | {user.real_name} | {role_display} | {'启用' if user.is_active else '禁用'} |\n"
    
    doc_content += """
---

## 二、会计员工账号

| 序号 | 用户名 | 邮箱 | 姓名 | 角色 | 状态 |
|------|--------|------|------|------|------|
"""
    
    role_map = {
        'accountant': '会计',
        'assistant': '助理',
        'manager': '主管',
    }
    
    all_staff = admin_users + accountant_users
    for i, user in enumerate(accountant_users, 1):
        doc_content += f"| {i} | {user.username} | {user.email} | {user.real_name} | {role_map.get(user.role, user.role)} | {'启用' if user.is_active else '禁用'} |\n"
    
    doc_content += """
---

## 三、客户账号

| 序号 | 客户编号 | 公司名称 | 用户名 | 联系人 | 行业 | 纳税类型 | 服务费用(円) | 状态 |
|------|----------|----------|--------|--------|------|----------|--------------|------|
"""
    
    tax_type_map = {
        'small_scale': '小规模纳税人',
        'general': '一般纳税人',
    }
    
    for i, (user, customer) in enumerate(zip(customer_users, customers), 1):
        doc_content += f"| {i} | {customer.customer_code} | {customer.company_name} | {user.username} | {customer.representative_name} | {customer.industry} | {tax_type_map.get(customer.tax_type, customer.tax_type)} | {customer.service_fee:,.0f} | {'启用' if customer.is_active else '禁用'} |\n"
    
    doc_content += """
---

## 四、客户详细信息

"""
    
    for customer in customers:
        doc_content += f"""### {customer.customer_code} - {customer.company_name}

- **公司类型**: {customer.company_type}
- **行业**: {customer.industry}
- **代表者**: {customer.representative_name}
- **联系电话**: {customer.phone_number}
- **邮箱**: {customer.contact_email}
- **地址**: {customer.address}
- **法人番号**: {customer.tax_number}
- **纳税人识别号**: {customer.tax_id}
- **所属税务局**: {customer.tax_bureau}
- **纳税人类型**: {tax_type_map.get(customer.tax_type, customer.tax_type)}
- **服务开始日期**: {customer.service_start_date}
- **服务费用**: {customer.service_fee:,.0f} 円/月
- **服务周期**: 按月

---

"""
    
    doc_content += """## 五、测试报表数据

报表期间: 2024年10月 - 2025年3月 (共6个月)

每个客户包含以下报表类型:
- 月次報告書 (monthly)
- 貸借対照表 (balance_sheet)
- 損益計算書 (income_statement)
- 明細帳 (detail_ledger)

报表状态分布:
- 草稿 (draft)
- 已提交 (submitted)
- 已审核 (reviewed)
- 已批准 (approved)

---

## 六、登录日志数据

每个客户账号包含:
- 5-10条登录记录
- 包含成功和失败的登录尝试
- 模拟不同设备和浏览器
- 时间范围: 最近90天

---

## 七、使用说明

### 登录方式
1. 打开系统登录页面
2. 输入用户名和密码
3. 点击登录按钮

### 测试场景建议
1. **管理员测试**: 使用 admin 或 admin2 登录，测试客户管理、报表管理、用户管理功能
2. **会计测试**: 使用 accountant1 或 accountant2 登录，测试客户服务和报表处理功能
3. **客户测试**: 使用 CUST001 - CUST012 登录，测试客户自助服务功能

### 注意事项
- 所有账号使用统一密码: `{password}`
- 测试数据仅供开发和测试使用
- 请勿在生产环境使用这些测试账号

---

*文档生成时间: {datetime}*
""".format(password=DEFAULT_PASSWORD, datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return doc_content


def init_test_data():
    """初始化所有测试数据"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("代理记账客户管理系统 - 测试数据初始化")
        print("=" * 60)
        
        # 清空现有数据
        print("\n[1/7] 清空现有数据...")
        db.drop_all()
        print("    ✓ 数据库表已删除")
        
        # 创建新表
        print("\n[2/7] 创建数据库表...")
        db.create_all()
        print("    ✓ 数据库表创建成功")
        
        # 创建管理员账号
        print("\n[3/7] 创建管理员账号...")
        admin_users = create_admin_users()
        db.session.commit()
        print(f"    ✓ 创建了 {len(admin_users)} 个管理员账号")
        
        # 创建会计员工账号
        print("\n[4/7] 创建会计员工账号...")
        accountant_users = create_accountant_users()
        db.session.commit()
        print(f"    ✓ 创建了 {len(accountant_users)} 个会计员工账号")
        
        # 为客户创建用户账号
        print("\n[5/7] 创建客户用户账号...")
        customer_users = create_customer_users()
        db.session.commit()
        print(f"    ✓ 创建了 {len(customer_users)} 个客户账号")
        
        # 创建客户数据
        print("\n[6/7] 创建客户详细信息...")
        all_staff = admin_users + accountant_users
        customers = create_customers(customer_users, all_staff)
        db.session.commit()
        print(f"    ✓ 创建了 {len(customers)} 个客户")
        
        # 创建报表数据
        print("\n[7/7] 创建报表和登录日志数据...")
        reports = create_reports(customers, admin_users)
        logs = create_login_logs(customer_users)
        db.session.commit()
        print(f"    ✓ 创建了 {len(reports)} 个报表")
        print(f"    ✓ 创建了 {len(logs)} 条登录日志")
        
        # 生成测试账号清单文档
        print("\n[8/7] 生成测试账号清单文档...")
        doc_content = generate_test_account_document(admin_users, accountant_users, customer_users, customers)
        doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_accounts.md')
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        print(f"    ✓ 测试账号清单已保存: {doc_path}")
        
        # 打印汇总信息
        print("\n" + "=" * 60)
        print("测试数据初始化完成!")
        print("=" * 60)
        print(f"\n统计信息:")
        print(f"  - 管理员账号: {len(admin_users)} 个")
        print(f"  - 会计员工: {len(accountant_users)} 人")
        print(f"  - 客户数量: {len(customers)} 家")
        print(f"  - 报表数量: {len(reports)} 份")
        print(f"  - 登录日志: {len(logs)} 条")
        print(f"\n统一测试密码: {DEFAULT_PASSWORD}")
        print("\n管理员账号:")
        for user in admin_users:
            print(f"  - {user.username} ({user.real_name})")
        print("\n客户账号示例:")
        for user in customer_users[:3]:
            print(f"  - {user.username} ({user.real_name})")
        print(f"  ... 共 {len(customer_users)} 个客户账号")
        print("\n" + "=" * 60)


if __name__ == '__main__':
    init_test_data()
