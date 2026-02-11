from pydantic import BaseModel

from app.enums.order_status import OrderStatus

class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: OrderStatus