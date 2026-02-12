from pydantic import BaseModel, EmailStr, ConfigDict, Field
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


class UserUpdatePassword(BaseModel):
    """Schema para atualizar senha."""

    current_password: str
    new_password: str


class UserUpdateRole(BaseModel):
    """Schema para admin alterar role (admin only)."""

    role: UserRole


class UserUpdateStatus(BaseModel):
    """Schema para ativar/desativar usuário (admin only)."""

    is_active: bool


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


class UserFilter(BaseModel):
    """Filtros para busca de usuários."""

    role: UserRole | None = None
    is_active: bool | None = None
    search: str | None = None  # busca por name ou email
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
