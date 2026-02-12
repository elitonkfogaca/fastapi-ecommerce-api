from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import re

from app.models.categories import Category
from app.models.products import Product
from app.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service para lógica de negócio de categorias."""

    @staticmethod
    def generate_slug(name: str) -> str:
        """Gera slug a partir do nome."""
        # Remove acentos e caracteres especiais
        slug = name.lower()
        slug = re.sub(r"[àáâãäå]", "a", slug)
        slug = re.sub(r"[èéêë]", "e", slug)
        slug = re.sub(r"[ìíîï]", "i", slug)
        slug = re.sub(r"[òóôõö]", "o", slug)
        slug = re.sub(r"[ùúûü]", "u", slug)
        slug = re.sub(r"[ç]", "c", slug)
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug

    @staticmethod
    async def get_categories(db: AsyncSession) -> list[Category]:
        """Listar todas as categorias."""
        query = select(Category).order_by(Category.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_categories_with_count(db: AsyncSession) -> list[dict]:
        """Listar categorias com contagem de produtos."""
        query = (
            select(Category, func.count(Product.id).label("product_count"))
            .outerjoin(Product, Category.id == Product.category_id)
            .group_by(Category.id)
            .order_by(Category.name)
        )

        result = await db.execute(query)
        categories_with_count = []

        for category, count in result.all():
            category_dict = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "product_count": count,
            }
            categories_with_count.append(category_dict)

        return categories_with_count

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Category:
        """Buscar categoria por ID."""
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        return category

    @staticmethod
    async def get_category_by_slug(db: AsyncSession, slug: str) -> Category:
        """Buscar categoria por slug."""
        query = select(Category).where(Category.slug == slug)
        result = await db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        return category

    @staticmethod
    async def create_category(
        db: AsyncSession, category_in: CategoryCreate
    ) -> Category:
        """Criar nova categoria."""

        # Gerar slug
        slug = CategoryService.generate_slug(category_in.name)

        # Verificar se slug já existe
        existing_query = select(Category).where(Category.slug == slug)
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with similar name already exists",
            )

        # Criar categoria
        category = Category(name=category_in.name, slug=slug)
        db.add(category)
        await db.commit()
        await db.refresh(category)

        return category

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: int, category_in: CategoryUpdate
    ) -> Category:
        """Atualizar categoria."""

        category = await CategoryService.get_category_by_id(db, category_id)

        if category_in.name:
            # Gerar novo slug
            new_slug = CategoryService.generate_slug(category_in.name)

            # Verificar se slug já existe (exceto a própria categoria)
            existing_query = select(Category).where(
                Category.slug == new_slug, Category.id != category_id
            )
            existing_result = await db.execute(existing_query)
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with similar name already exists",
                )

            category.name = category_in.name
            category.slug = new_slug

        await db.commit()
        await db.refresh(category)

        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> None:
        """Deletar categoria."""

        category = await CategoryService.get_category_by_id(db, category_id)

        # Verificar se tem produtos associados
        products_query = select(Product).where(Product.category_id == category_id)
        products_result = await db.execute(products_query)
        if products_result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with associated products",
            )

        await db.delete(category)
        await db.commit()
