from app import app, db
from app.models import User
import getpass

def change_password():
    with app.app_context():
        username = input("Enter username (default: admin): ") or 'admin'
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found.")
            return
        
        new_password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("Passwords do not match.")
            return

        user.set_password(new_password)
        db.session.commit()
        print(f"Password for '{username}' has been updated successfully.")

if __name__ == '__main__':
    change_password()
