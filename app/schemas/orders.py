from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.enums.order_status import OrderStatus


class OrderItemCreate(BaseModel):
    """Item do pedido na criação."""

    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    """Resposta de item do pedido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float

    # Informações do produto
    product_name: str | None = None


class OrderCreate(BaseModel):
    """Schema para criar pedido."""

    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdateStatus(BaseModel):
    """Schema para atualizar status do pedido."""

    status: OrderStatus


class OrderResponse(BaseModel):
    """Schema de resposta do pedido."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_price: float
    status: OrderStatus
    created_at: datetime

    # User info
    user_name: str | None = None
    user_email: str | None = None

    # Items (opcional)
    items: list[OrderItemResponse] = []


class OrderFilter(BaseModel):
    """Filtros para busca de pedidos."""

    status: OrderStatus | None = None
    user_id: int | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
