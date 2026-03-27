# create_admin_user.py
# Script to create admin user in Supabase

from supabase_client import db
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin():
    """Create admin user in Supabase"""
    
    admin_data = {
        'name': 'Admin User',
        'email': 'admin@unihelp.com',
        'passwordhash': generate_password_hash('admin123'),
        'role': 'admin',
        'isapproved': True,
        'created_at': datetime.now().isoformat()
    }
    
    print("Creating admin user...")
    print(f"Email: {admin_data['email']}")
    print(f"Password: admin123")
    
    try:
        new_user = db.create_user(admin_data)
        if new_user:
            print("\n✅ SUCCESS! Admin user created!")
            print(f"User ID: {new_user.get('userid')}")
            print(f"Email: {new_user.get('email')}")
            print(f"Role: {new_user.get('role')}")
            print("\nYou can now login with:")
            print("  Email: admin@unihelp.com")
            print("  Password: admin123")
        else:
            print("\n❌ FAILED to create user")
            print("Check if email already exists or database connection")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        if 'UNIQUE constraint' in str(e) or 'duplicate' in str(e).lower():
            print("\n⚠️  User already exists! Try logging in directly.")

if __name__ == '__main__':
    create_admin()
