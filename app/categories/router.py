from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithProductCount,
)
from app.schemas.responses import SuccessResponse
from app.categories.service import CategoryService
from app.auth.dependencies import require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.get("", response_model=SuccessResponse[list[CategoryWithProductCount]])
async def list_categories(
    include_count: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Listar todas as categorias."""

    if include_count:
        categories = await CategoryService.get_categories_with_count(db)
        return SuccessResponse(
            data=categories, message="Categories retrieved successfully"
        )
    else:
        categories = await CategoryService.get_categories(db)
        return SuccessResponse(
            data=[CategoryResponse.model_validate(c) for c in categories],
            message="Categories retrieved successfully",
        )


@router.get("/{category_id}", response_model=SuccessResponse[CategoryResponse])
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Buscar categoria por ID."""

    category = await CategoryService.get_category_by_id(db, category_id)

    return SuccessResponse(
        data=CategoryResponse.model_validate(category),
        message="Category retrieved successfully",
    )


@router.get("/slug/{slug}", response_model=SuccessResponse[CategoryResponse])
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Buscar categoria por slug."""

    category = await CategoryService.get_category_by_slug(db, slug)

    return SuccessResponse(
        data=CategoryResponse.model_validate(category),
        message="Category retrieved successfully",
    )


@router.post("", response_model=SuccessResponse[CategoryResponse])
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Criar categoria (apenas admin)."""

    category = await CategoryService.create_category(db, category_in)

    return SuccessResponse(
        data=CategoryResponse.model_validate(category),
        message="Category created successfully",
    )


@router.put("/{category_id}", response_model=SuccessResponse[CategoryResponse])
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar categoria (apenas admin)."""

    category = await CategoryService.update_category(db, category_id, category_in)

    return SuccessResponse(
        data=CategoryResponse.model_validate(category),
        message="Category updated successfully",
    )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletar categoria (apenas admin)."""

    await CategoryService.delete_category(db, category_id)

    return SuccessResponse(data=None, message="Category deleted successfully")
