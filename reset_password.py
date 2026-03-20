from app import create_app
from app.models import db
from app.models.user import User

app = create_app('development')
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'Resetting password for admin user...')
        admin.set_password('Test@123456')
        db.session.commit()
        print(f'Password reset successfully!')
        # Verify
        test_result = admin.check_password('Test@123456')
        print(f'Password verification: {test_result}')
    else:
        print('Admin user not found! Creating new admin user...')
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_active=True,
            is_admin=True
        )
        admin.set_password('Test@123456')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
