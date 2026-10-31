import uuid
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.security import hash_password
from app.models.user import User, Customer, UserRole
from app.schemas.user import StaffCreateRequest, UserUpdateRequest


class UserService:
    @staticmethod
    def create_staff(db: Session, data: StaffCreateRequest) -> User:
        """Admin creates a staff account."""
        normalized_email = data.email.strip().lower()
        
        existing = db.query(User).filter(User.email == normalized_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        new_staff = User(
            full_name=data.full_name.strip(),
            email=normalized_email,
            password_hash=hash_password(data.password),
            role=UserRole.STAFF,
            is_active=True,
        )
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        return new_staff

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> User:
        """Retrieve a user by their UUID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def list_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        role: Optional[UserRole] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        """Query users with optional role filtering and full-name/email search."""
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(User.full_name.ilike(search_term), User.email.ilike(search_term))
            )
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_profile(db: Session, user: User, data: UserUpdateRequest) -> User:
        """Update user profile and customer profile information."""
        if data.full_name is not None and data.full_name.strip():
            user.full_name = data.full_name.strip()

        # Update customer profile if present or create if customer
        if any([data.company_name is not None, data.phone is not None, data.address is not None]):
            if not user.customer_profile:
                customer_profile = Customer(user_id=user.id)
                db.add(customer_profile)
                user.customer_profile = customer_profile
            
            if data.company_name is not None:
                user.customer_profile.company_name = data.company_name.strip()
            if data.phone is not None:
                user.customer_profile.phone = data.phone.strip()
            if data.address is not None:
                user.customer_profile.address = data.address.strip()

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_status(
        db: Session, 
        target_user_id: uuid.UUID, 
        is_active: bool, 
        admin_id: uuid.UUID
    ) -> User:
        """Activate or deactivate a user account."""
        if target_user_id == admin_id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot deactivate their own account.",
            )

        user = UserService.get_by_id(db, target_user_id)
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user


user_service = UserService()
