from app import app, db
from app.models import User

def create_admin():
    with app.app_context():
        if User.query.filter_by(username='admin').first():
            print("Admin user already exists.")
            return
        
        user = User(username='admin', email='admin@example.com')
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()
        print("Admin user created with username 'admin' and password 'admin'.")

if __name__ == '__main__':
    create_admin()
