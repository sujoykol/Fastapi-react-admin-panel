from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.admin import Admin


ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin123@#"


def seed_admin():
    db = SessionLocal()

    try:
        existing_admin = db.scalar(
            select(Admin).where(
                Admin.username == ADMIN_USERNAME
            )
        )

        if existing_admin:
            print("Admin already exists.")
            return

        admin = Admin(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")
        print(f"Username: {ADMIN_USERNAME}")
        print(f"Email: {ADMIN_EMAIL}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
