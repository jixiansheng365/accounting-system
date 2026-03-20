#!/usr/bin/env python3
"""检查翻译是否正确加载"""
import requests

BASE_URL = "http://127.0.0.1:5001"

session = requests.Session()

# 登录
session.get(f'{BASE_URL}/auth/login?lang=zh_CN')
login_data = {'username': 'admin', 'password': 'Test@123456'}
session.post(f'{BASE_URL}/auth/login', data=login_data)

# 获取系统设置页面
r = session.get(f'{BASE_URL}/admin/settings')
html = r.text

# 检查关键翻译
translations_to_check = [
    ('Total Users', '总用户数'),
    ('Active Users', '活跃用户'),
    ('Admin Users', '管理员用户'),
    ('System Configuration', '系统配置'),
    ('Application Name', '应用名称'),
    ('Debug Mode', '调试模式'),
    ('Database', '数据库'),
    ('Max Upload Size', '最大上传大小'),
    ('Allowed File Types', '允许的文件类型'),
    ('Session Lifetime', '会话有效期'),
    ('System Operations', '系统操作'),
    ('Database Backup', '数据库备份'),
    ('Backup system database', '备份系统数据库'),
    ('Backup', '备份'),
    ('Clear Cache', '清除缓存'),
    ('Clear system cache', '清除系统缓存'),
    ('Clear', '清除'),
]

print("翻译检查结果:")
print("=" * 50)

for en, zh in translations_to_check:
    if zh in html:
        print(f"✅ {en} -> {zh}")
    elif en in html:
        print(f"❌ {en} 未翻译")
    else:
        print(f"⚠️  {en} 未找到")

print("=" * 50)
