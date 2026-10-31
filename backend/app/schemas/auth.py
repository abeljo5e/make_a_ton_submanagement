from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.user import UserResponse
from app.core.security import validate_password_strength


class CustomerRegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

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


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        is_valid, err_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(err_msg)
        return v


class MessageResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    reset_token_preview: Optional[str] = None  # Preview provided in development mode only
