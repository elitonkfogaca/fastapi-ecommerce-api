from sqlalchemy import String, Boolean, DateTime, func, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float(), nullable=False)
    stock: Mapped[int] = mapped_column(Integer(), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer(), ForeignKey('categories.id'), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    update_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())