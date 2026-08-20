from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.core.database import get_db
from app.models.admin import Admin
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.login(
        username=request.username,
        password=request.password,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.refresh_access_token(
        request.refresh_token
    )


@router.get("/me")
def get_me(
    admin: Admin = Depends(get_current_admin),
):
    return {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
        "is_active": admin.is_active,
    }


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.change_password(
        admin=admin,
        current_password=request.current_password,
        new_password=request.new_password,
    )

@router.post("/logout")
def logout(
    admin: Admin = Depends(get_current_admin),
):
    return {
        "message": "Logout successful"
    }    