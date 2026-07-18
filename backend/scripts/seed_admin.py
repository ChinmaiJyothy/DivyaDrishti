"""Seed a dedicated verification admin user."""
import os
import sys
from datetime import datetime, timezone

# Ensure we use the same database as the backend server before importing backend modules
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend', 'divyadrishti.db')}"

backend_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, backend_src)

from divyadrishti.config import get_settings
from divyadrishti.database.database import SessionLocal, engine, Base
from divyadrishti.models import Role, User
from divyadrishti.security.password import hash_password

EMAIL = "admin@example.com"
PASSWORD = "TestPass123!"
NAME = "Verification Admin"


def seed():
    settings = get_settings()
    db = SessionLocal()
    try:
        # Ensure admin role exists
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN")
            db.add(admin_role)
            db.flush()

        user = db.query(User).filter(User.email == EMAIL).first()
        if not user:
            user = User(
                email=EMAIL,
                name=NAME,
                hashed_password=hash_password(PASSWORD),
                role_id=admin_role.id,
                is_superuser=True,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
        else:
            user.name = NAME
            user.hashed_password = hash_password(PASSWORD)
            user.is_superuser = True
            user.is_active = True
            user.is_verified = True
            user.role_id = admin_role.id
            user.updated_at = datetime.now(timezone.utc)
        db.commit()
        print(f"Seeded admin user: {EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
