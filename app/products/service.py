from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.products import Product
from app.models.categories import Category
from app.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductUpdateStock,
    ProductFilter,
)


class ProductService:
    """Service para lógica de negócio de produtos."""

    @staticmethod
    async def get_products(
        db: AsyncSession, filters: ProductFilter
    ) -> tuple[list[Product], int]:
        """Buscar produtos com filtros e paginação."""

        # Base query com join de category
        query = select(Product).options(selectinload(Product.category))

        # Aplicar filtros
        conditions = []

        if filters.name:
            conditions.append(Product.name.ilike(f"%{filters.name}%"))

        if filters.category_id:
            conditions.append(Product.category_id == filters.category_id)

        if filters.min_price is not None:
            conditions.append(Product.price >= filters.min_price)

        if filters.max_price is not None:
            conditions.append(Product.price <= filters.max_price)

        conditions.append(Product.is_active == filters.is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(Product.id).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = len(total_result.all())

        # Paginação
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Ordenar por nome
        query = query.order_by(Product.name)

        result = await db.execute(query)
        products = result.scalars().all()

        return list(products), total

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: int) -> Product:
        """Buscar produto por ID."""
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )

        result = await db.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        return product

    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
        """Criar novo produto."""

        # Validar se categoria existe
        category_query = select(Category).where(Category.id == product_in.category_id)
        category_result = await db.execute(category_query)
        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Criar produto
        product = Product(**product_in.model_dump())
        db.add(product)
        await db.commit()
        await db.refresh(product)

        # Carregar relationship
        await db.refresh(product, ["category"])

        return product

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: int, product_in: ProductUpdate
    ) -> Product:
        """Atualizar produto."""

        product = await ProductService.get_product_by_id(db, product_id)

        # Validar categoria se foi alterada
        if product_in.category_id and product_in.category_id != product.category_id:
            category_query = select(Category).where(
                Category.id == product_in.category_id
            )
            category_result = await db.execute(category_query)
            if not category_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

        # Atualizar apenas campos fornecidos
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        await db.commit()
        await db.refresh(product)
        await db.refresh(product, ["category"])

        return product

    @staticmethod
    async def update_stock(
        db: AsyncSession, product_id: int, stock_in: ProductUpdateStock
    ) -> Product:
        """Atualizar estoque do produto."""

        product = await ProductService.get_product_by_id(db, product_id)
        product.stock = stock_in.stock

        await db.commit()
        await db.refresh(product)
        await db.refresh(product, ["category"])

        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> Product:
        """Desativar produto (soft delete)."""

        product = await ProductService.get_product_by_id(db, product_id)
        product.is_active = False

        await db.commit()
        await db.refresh(product)

        return product
