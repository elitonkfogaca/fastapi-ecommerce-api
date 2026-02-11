from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"