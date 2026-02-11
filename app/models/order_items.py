from sqlalchemy import Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer(), ForeignKey('orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer(), ForeignKey('products.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float(), nullable=False)