import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from app.models.user import UserRole
from app.core.security import validate_password_strength


class CustomerProfileBase(BaseModel):
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerProfileResponse(CustomerProfileBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    full_name: str
    email: str


class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    customer_profile: Optional[CustomerProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class StaffCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        is_valid, err_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(err_msg)
        return v

    @field_validator("email")
    @classmethod
    def check_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return v
