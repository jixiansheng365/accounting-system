"""
修复 admin 用户密码脚本
将 admin 用户密码设置为 admin123
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User

def fix_admin_password():
    """修复 admin 用户密码"""
    app = create_app()
    
    with app.app_context():
        # 查找 admin 用户
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            # 设置新密码
            admin.set_password('admin123')
            db.session.commit()
            print(f"✅ Admin 用户密码已更新为: admin123")
            print(f"   用户ID: {admin.id}")
            print(f"   用户名: {admin.username}")
            print(f"   邮箱: {admin.email}")
            print(f"   角色: {admin.role}")
        else:
            # 创建 admin 用户
            admin = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin 用户已创建")
            print(f"   用户名: admin")
            print(f"   密码: admin123")
            print(f"   角色: admin")
        
        # 验证密码
        if admin.check_password('admin123'):
            print("\n✅ 密码验证成功！")
        else:
            print("\n❌ 密码验证失败！")

if __name__ == '__main__':
    fix_admin_password()
