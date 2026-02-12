"""
Script para popular o banco de dados com dados iniciais.
Execute: python -m app.database.seed
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.models.user import User
from app.models.categories import Category
from app.enums.user_role import UserRole
from app.auth.security import get_password_hash


async def create_admin_user(db: AsyncSession) -> User:
    """Cria usuário admin padrão."""

    # Verificar se já existe admin
    result = await db.execute(select(User).where(User.email == "admin@example.com"))
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        print("✅ Admin user already exists")
        return existing_admin

    # Criar admin
    admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    print("✅ Admin user created successfully")
    print(f"   Email: {admin.email}")
    print(f"   Password: admin123")
    print("   ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")

    return admin


async def create_sample_categories(db: AsyncSession) -> list[Category]:
    """Cria categorias de exemplo."""

    categories_data = [
        {"name": "Eletrônicos", "slug": "eletronicos"},
        {"name": "Roupas", "slug": "roupas"},
        {"name": "Livros", "slug": "livros"},
        {"name": "Casa e Decoração", "slug": "casa-e-decoracao"},
        {"name": "Esportes", "slug": "esportes"},
    ]

    created_categories = []

    for cat_data in categories_data:
        # Verificar se já existe
        result = await db.execute(
            select(Category).where(Category.slug == cat_data["slug"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"   Category '{cat_data['name']}' already exists")
            created_categories.append(existing)
            continue

        category = Category(**cat_data)
        db.add(category)
        created_categories.append(category)
        print(f"   Created category: {cat_data['name']}")

    await db.commit()

    return created_categories


async def create_sample_user(db: AsyncSession) -> User:
    """Cria usuário comum de exemplo."""

    # Verificar se já existe
    result = await db.execute(select(User).where(User.email == "customer@example.com"))
    existing = result.scalar_one_or_none()

    if existing:
        print("✅ Sample customer already exists")
        return existing

    customer = User(
        name="Customer Test",
        email="customer@example.com",
        password_hash=get_password_hash("customer123"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    print("✅ Sample customer created")
    print(f"   Email: {customer.email}")
    print(f"   Password: customer123")

    return customer


async def seed_database():
    """Função principal para popular o banco."""

    print("\n🌱 Starting database seeding...\n")

    async with AsyncSessionLocal() as db:
        try:
            # Criar admin
            print("1️⃣ Creating admin user...")
            await create_admin_user(db)

            # Criar usuário de exemplo
            print("\n2️⃣ Creating sample customer...")
            await create_sample_user(db)

            # Criar categorias de exemplo
            print("\n3️⃣ Creating sample categories...")
            categories = await create_sample_categories(db)
            print(f"✅ {len(categories)} categories ready")

            print("\n✅ Database seeded successfully!\n")

        except Exception as e:
            print(f"\n❌ Error seeding database: {str(e)}\n")
            await db.rollback()
            raise


async def seed_only_admin():
    """Seed apenas do admin (sem dados de exemplo)."""

    print("\n🌱 Creating admin user only...\n")

    async with AsyncSessionLocal() as db:
        try:
            await create_admin_user(db)
            print("\n✅ Admin created successfully!\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            await db.rollback()
            raise


if __name__ == "__main__":
    # Executar seed completo
    asyncio.run(seed_database())

    # Para seed apenas do admin, use:
    # asyncio.run(seed_only_admin())
