"""
Script to create an admin user in the database
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime


def create_admin_user(
    username: str = "admin",
    password: str = "admin123",
    email: str = "admin@clientmonitor.com",
    full_name: str = "System Administrator"
):
    """Create an admin user in the database."""

    db: Session = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == username.lower()).first()

        if existing_admin:
            print(f"[X] User '{username}' already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Is Superuser: {existing_admin.is_superuser}")
            return False

        # Create admin user
        admin_user = User(
            username=username.lower(),
            email=email.lower(),
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("[OK] Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: {password}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        print(f"\n[!] Please change the password after first login!")

        return True

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating admin user: {e}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Creating System Administrator Account")
    print("=" * 60)
    print()

    # You can customize these values
    create_admin_user(
        username="admin",
        password="admin123",
        email="admin@clientmonitor.com",
        full_name="System Administrator"
    )

    print()
    print("=" * 60)
