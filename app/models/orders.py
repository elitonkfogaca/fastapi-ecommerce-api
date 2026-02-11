from sqlalchemy import Integer, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.enums.order_status import OrderStatus


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey('users.id'))
    total_price: Mapped[float] = mapped_column(Float(), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False)
