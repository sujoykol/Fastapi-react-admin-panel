from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.admin import Admin


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def login(
        self,
        username: str,
        password: str,
    ) -> dict:

        statement = select(Admin).where(
            Admin.username == username
        )

        admin = self.db.scalar(statement)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive",
            )

        if not verify_password(
            password,
            admin.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        access_token = create_access_token(admin.id)
        refresh_token = create_refresh_token(admin.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> dict:

        admin_id = decode_refresh_token(refresh_token)

        statement = select(Admin).where(
            Admin.id == admin_id
        )

        admin = self.db.scalar(statement)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found",
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive",
            )

        access_token = create_access_token(admin.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def change_password(
        self,
        admin: Admin,
        current_password: str,
        new_password: str,
        ) -> dict:

        if not verify_password(
            current_password,
            admin.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different",
            )

        admin.password_hash = hash_password(new_password)

        self.db.commit()

        return {
            "message": "Password changed successfully"
        }    