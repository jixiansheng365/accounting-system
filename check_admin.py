from app import create_app
from app.models import db
from app.models.user import User

app = create_app('development')
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'Admin user found: {admin.username}')
        print(f'Role: {admin.role}')
        print(f'Is active: {admin.is_active}')
        # Test password
        test_result = admin.check_password('Test@123456')
        print(f'Password test: {test_result}')
    else:
        print('Admin user not found!')
        # List all users
        users = User.query.all()
        print(f'Total users: {len(users)}')
        for u in users:
            print(f'  - {u.username} ({u.role})')
