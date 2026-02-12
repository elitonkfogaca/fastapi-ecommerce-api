from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user import (
    UserUpdate,
    UserUpdatePassword,
    UserUpdateRole,
    UserUpdateStatus,
    UserResponse,
    UserFilter,
)
from app.schemas.responses import SuccessResponse, PaginatedResponse
from app.users.service import UserService
from app.auth.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.enums.user_role import UserRole

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    role: UserRole | None = Query(None, description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Listar usuários (apenas admin)."""

    filters = UserFilter(
        role=role, is_active=is_active, search=search, page=page, page_size=page_size
    )

    users, total = await UserService.get_users(db, filters)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Buscar usuário por ID (próprio usuário ou admin)."""

    # Verifica se é admin ou o próprio usuário
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user",
        )

    user = await UserService.get_user_by_id(db, user_id)

    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar dados do usuário (próprio usuário ou admin)."""

    # Verifica se é admin ou o próprio usuário
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    user = await UserService.update_user(db, user_id, user_in, current_user.id)

    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User updated successfully"
    )


@router.patch("/{user_id}/password", response_model=SuccessResponse[UserResponse])
async def update_password(
    user_id: int,
    password_in: UserUpdatePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar senha (apenas o próprio usuário)."""

    # Apenas o próprio usuário pode alterar sua senha
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to change this user's password",
        )

    user = await UserService.update_password(db, user_id, password_in)

    return SuccessResponse(
        data=UserResponse.model_validate(user), message="Password updated successfully"
    )


@router.patch("/{user_id}/role", response_model=SuccessResponse[UserResponse])
async def update_user_role(
    user_id: int,
    role_in: UserUpdateRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar role do usuário (apenas admin)."""

    # Admin não pode alterar o próprio role
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    user = await UserService.update_role(db, user_id, role_in)

    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User role updated successfully"
    )


@router.patch("/{user_id}/status", response_model=SuccessResponse[UserResponse])
async def update_user_status(
    user_id: int,
    status_in: UserUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Ativar/desativar usuário (apenas admin)."""

    # Admin não pode desativar a si mesmo
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status",
        )

    user = await UserService.update_status(db, user_id, status_in)

    return SuccessResponse(
        data=UserResponse.model_validate(user),
        message="User status updated successfully",
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletar usuário (apenas admin)."""

    # Admin não pode deletar a si mesmo
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )

    await UserService.delete_user(db, user_id)

    return SuccessResponse(data=None, message="User deleted successfully")
