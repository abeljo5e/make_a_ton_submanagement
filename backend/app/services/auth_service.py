from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    generate_reset_token,
    hash_reset_token,
)
from app.models.user import User, Customer, PasswordResetToken, UserRole, utc_now
from app.schemas.auth import CustomerRegisterRequest


class AuthService:
    @staticmethod
    def register_customer(db: Session, data: CustomerRegisterRequest) -> User:
        """Register a new customer account atomically."""
        normalized_email = data.email.strip().lower()
        
        # Check existing user
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists.",
            )

        hashed_pwd = hash_password(data.password)

        new_user = User(
            full_name=data.full_name.strip(),
            email=normalized_email,
            password_hash=hashed_pwd,
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        db.add(new_user)
        db.flush()  # Populates new_user.id

        customer_profile = Customer(
            user_id=new_user.id,
            company_name=data.company_name.strip() if data.company_name else None,
            phone=data.phone.strip() if data.phone else None,
            address=data.address.strip() if data.address else None,
        )
        db.add(customer_profile)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Verify user credentials and active state."""
        normalized_email = email.strip().lower()
        user = db.query(User).filter(User.email == normalized_email).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Please contact support.",
            )
            
        return user

    @staticmethod
    def create_password_reset_token(db: Session, email: str) -> Tuple[bool, Optional[str]]:
        """Generate a single-use expiring password reset token for the given email."""
        normalized_email = email.strip().lower()
        user = db.query(User).filter(User.email == normalized_email).first()
        
        # For security, avoid leaking whether the email exists
        if not user or not user.is_active:
            return False, None

        # Invalidate previous unused reset tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False,
        ).update({"is_used": True})

        raw_token, token_hash = generate_reset_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )

        reset_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False,
        )
        db.add(reset_record)
        db.commit()

        # In a production environment with SMTP configured, this would send an email.
        # We return the raw_token to allow preview/testing in dev environments.
        return True, raw_token

    @staticmethod
    def reset_password(db: Session, raw_token: str, new_password: str) -> User:
        """Validate reset token and update the user's password."""
        token_hash = hash_reset_token(raw_token)
        now = datetime.now(timezone.utc)

        token_record = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > now,
            )
            .first()
        )

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid, used, or expired password reset token.",
            )

        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found for this reset token.",
            )

        user.password_hash = hash_password(new_password)
        token_record.is_used = True
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
