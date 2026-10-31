from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_current_active_user,
)
from app.models.user import User
from app.schemas.auth import (
    CustomerRegisterRequest,
    LoginRequest,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.auth_service import auth_service
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account",
)
def register(
    data: CustomerRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new customer.
    Validates email format, uniqueness, and password complexity rules.
    Automatically assigns role 'customer' and creates customer profile.
    """
    user = auth_service.register_customer(db, data)
    return user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and obtain JWT token",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user using email and password.
    Returns a signed JWT bearer token and user profile.
    """
    user = auth_service.authenticate_user(db, data.email, data.password)
    token_str = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )
    return Token(
        access_token=token_str,
        token_type="bearer",
        user=user,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user session",
)
def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Acknowledge client-side token invalidation.
    """
    return MessageResponse(
        detail=f"User {current_user.email} successfully logged out."
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve profile details, customer details, and role for the currently logged-in user.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current authenticated user profile",
)
def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update profile and contact information for the current user.
    """
    return user_service.update_profile(db, current_user, data)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset token",
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Initiate a password reset flow.
    Generates a hashed single-use token expiring in 15 minutes.
    In development mode, the preview token is returned in the response for testing.
    """
    success, raw_token = auth_service.create_password_reset_token(db, data.email)
    
    preview = None
    if settings.APP_ENV == "development" and raw_token:
        preview = raw_token

    return MessageResponse(
        detail="If an account exists with this email address, a password reset link has been dispatched.",
        reset_token_preview=preview,
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password using reset token",
)
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Consume the single-use reset token and set a new password.
    Validates new password complexity.
    """
    auth_service.reset_password(db, data.token, data.new_password)
    return MessageResponse(detail="Password has been successfully reset. You may now log in.")
