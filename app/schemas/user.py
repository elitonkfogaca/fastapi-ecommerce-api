from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

from app.enums.user_role import UserRole


class UserCreate(BaseModel):
    """Schema para criação de usuário."""

    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema para login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""

    name: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    """Schema de resposta de usuário (sem senha)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
