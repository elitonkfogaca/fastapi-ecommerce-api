from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import (
    UserUpdate,
    UserUpdatePassword,
    UserUpdateRole,
    UserUpdateStatus,
    UserFilter,
)
from app.auth.security import get_password_hash, verify_password
from app.enums.user_role import UserRole


class UserService:
    """Service para lógica de negócio de usuários."""

    @staticmethod
    async def get_users(
        db: AsyncSession, filters: UserFilter
    ) -> tuple[list[User], int]:
        """Buscar usuários com filtros e paginação."""

        query = select(User)

        # Aplicar filtros
        conditions = []

        if filters.role:
            conditions.append(User.role == filters.role)

        if filters.is_active is not None:
            conditions.append(User.is_active == filters.is_active)

        if filters.search:
            search_pattern = f"%{filters.search}%"
            conditions.append(
                or_(User.name.ilike(search_pattern), User.email.ilike(search_pattern))
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(User.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = len(total_result.all())

        # Paginação
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Ordenar por nome
        query = query.order_by(User.name)

        result = await db.execute(query)
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Buscar usuário por ID."""
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_in: UserUpdate, current_user_id: int
    ) -> User:
        """Atualizar dados do usuário."""

        user = await UserService.get_user_by_id(db, user_id)

        # Validar se é o próprio usuário ou admin
        # (essa validação também pode ficar no router)

        # Verificar email já existe (se for alterar)
        if user_in.email and user_in.email != user.email:
            email_query = select(User).where(User.email == user_in.email)
            email_result = await db.execute(email_query)
            if email_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )

        # Atualizar campos
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def update_password(
        db: AsyncSession, user_id: int, password_in: UserUpdatePassword
    ) -> User:
        """Atualizar senha do usuário."""

        user = await UserService.get_user_by_id(db, user_id)

        # Verificar senha atual
        if not verify_password(password_in.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Atualizar senha
        user.password_hash = get_password_hash(password_in.new_password)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def update_role(
        db: AsyncSession, user_id: int, role_in: UserUpdateRole
    ) -> User:
        """Atualizar role do usuário (admin only)."""

        user = await UserService.get_user_by_id(db, user_id)

        user.role = role_in.role

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def update_status(
        db: AsyncSession, user_id: int, status_in: UserUpdateStatus
    ) -> User:
        """Ativar/desativar usuário (admin only)."""

        user = await UserService.get_user_by_id(db, user_id)

        user.is_active = status_in.is_active

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        """Deletar usuário (admin only)."""

        user = await UserService.get_user_by_id(db, user_id)

        # Verificar se tem pedidos
        # (Opcional: pode fazer soft delete ao invés de hard delete)

        await db.delete(user)
        await db.commit()
