#!/usr/bin/env python
import argparse
import getpass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, Admin

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def create_superuser(phone_number: str, full_name: str, password: str = None):
    """Create a superuser (admin) for the API"""
    if not password:
        # If no password provided, prompt securely
        password = getpass.getpass("Enter password for superuser: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Passwords do not match!")
            return False
            
    # Validate phone number format
    if not phone_number.startswith("+998") or len(phone_number) != 13 or not phone_number[4:].isdigit():
        print("Phone number must be in format +998XXXXXXXXX")
        return False
        
    # Start database session
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.phone_number == phone_number).first()
        if existing_user:
            print(f"User with phone number {phone_number} already exists.")
            return False
            
        # Create user with admin type
        new_user = User(
            phone_number=phone_number,
            full_name=full_name,
            password_hash=hash_password(password),
            user_type="admin"
        )
        db.add(new_user)
        db.flush()  # Flush to get the user ID
        
        # Create admin profile with super_admin role
        new_admin = Admin(
            user_id=new_user.id,
            role="super_admin"
        )
        db.add(new_admin)
        db.commit()
        
        print(f"Superuser {full_name} ({phone_number}) created successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error creating superuser: {str(e)}")
        return False
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Create a superuser for NewEdu API")
    parser.add_argument("--phone", "-p", required=True, help="Phone number in format +998XXXXXXXXX")
    parser.add_argument("--name", "-n", required=True, help="Full name of the superuser")
    parser.add_argument("--password", help="Password (if not provided, will prompt)")
    
    args = parser.parse_args()
    create_superuser(args.phone, args.name, args.password)

if __name__ == "__main__":
    main()
