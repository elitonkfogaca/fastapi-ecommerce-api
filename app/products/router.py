from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductUpdateStock,
    ProductResponse,
    ProductFilter,
)
from app.schemas.responses import SuccessResponse, PaginatedResponse
from app.products.service import ProductService
from app.auth.dependencies import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    name: str | None = Query(None, description="Filter by product name"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    is_active: bool = Query(True, description="Filter active/inactive products"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """Listar produtos com filtros e paginação."""

    filters = ProductFilter(
        name=name,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    products, total = await ProductService.get_products(db, filters)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Buscar produto por ID."""

    product = await ProductService.get_product_by_id(db, product_id)

    return SuccessResponse(
        data=ProductResponse.model_validate(product),
        message="Product retrieved successfully",
    )


@router.post("", response_model=SuccessResponse[ProductResponse])
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Criar produto (apenas admin)."""

    product = await ProductService.create_product(db, product_in)

    return SuccessResponse(
        data=ProductResponse.model_validate(product),
        message="Product created successfully",
    )


@router.put("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar produto (apenas admin)."""

    product = await ProductService.update_product(db, product_id, product_in)

    return SuccessResponse(
        data=ProductResponse.model_validate(product),
        message="Product updated successfully",
    )


@router.patch("/{product_id}/stock", response_model=SuccessResponse[ProductResponse])
async def update_product_stock(
    product_id: int,
    stock_in: ProductUpdateStock,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar estoque do produto (apenas admin)."""

    product = await ProductService.update_stock(db, product_id, stock_in)

    return SuccessResponse(
        data=ProductResponse.model_validate(product),
        message="Stock updated successfully",
    )


@router.delete("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Desativar produto (apenas admin)."""

    product = await ProductService.delete_product(db, product_id)

    return SuccessResponse(
        data=ProductResponse.model_validate(product),
        message="Product deactivated successfully",
    )
