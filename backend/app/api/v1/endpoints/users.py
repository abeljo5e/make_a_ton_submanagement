import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import require_admin, require_staff, get_current_active_user
from app.models.user import User, UserRole
from app.schemas.user import (
    UserResponse,
    StaffCreateRequest,
    UserUpdateRequest,
    UserStatusUpdate,
)
from app.services.user_service import user_service

router = APIRouter(tags=["User Management"])


@router.post(
    "/staff",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin creates internal staff member",
)
@router.post(
    "/users/staff",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_staff_user(
    data: StaffCreateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new staff user. Enforces Admin-only authorization.
    """
    staff_user = user_service.create_staff(db, data)
    return staff_user


@router.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users with optional role filtering and search",
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    """
    List registered users. Accessible by Admin and Staff.
    """
    return user_service.list_users(db, skip=skip, limit=limit, role=role, search=search)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user details by ID",
)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve user details. Customers can only view their own record; Admins/Staff can view any.
    """
    if current_user.role == UserRole.CUSTOMER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You cannot view other user records.",
        )
    return user_service.get_by_id(db, user_id)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin updates user profile",
)
def update_user(
    user_id: uuid.UUID,
    data: UserUpdateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Administrative update of user and customer profile.
    """
    target_user = user_service.get_by_id(db, user_id)
    return user_service.update_profile(db, target_user, data)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin activates or deactivates user account",
)
def update_user_status(
    user_id: uuid.UUID,
    status_data: UserStatusUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Toggle user active status. Admins cannot deactivate their own account.
    """
    return user_service.update_user_status(
        db, target_user_id=user_id, is_active=status_data.is_active, admin_id=current_admin.id
    )
