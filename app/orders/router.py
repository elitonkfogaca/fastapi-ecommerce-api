from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.orders import (
    OrderCreate,
    OrderUpdateStatus,
    OrderResponse,
    OrderItemResponse,
    OrderFilter,
)
from app.schemas.responses import SuccessResponse, PaginatedResponse
from app.orders.service import OrderService
from app.auth.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.enums.order_status import OrderStatus
from app.enums.user_role import UserRole

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    status: OrderStatus | None = Query(None, description="Filter by status"),
    user_id: int | None = Query(None, description="Filter by user (admin only)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Listar pedidos (usuário vê apenas seus pedidos, admin vê todos)."""

    filters = OrderFilter(
        status=status,
        user_id=user_id if current_user.role == UserRole.ADMIN else None,
        page=page,
        page_size=page_size,
    )

    # Se não for admin, força filtro por user
    current_user_filter = (
        None if current_user.role == UserRole.ADMIN else current_user.id
    )

    orders, total = await OrderService.get_orders(db, filters, current_user_filter)

    total_pages = (total + page_size - 1) // page_size

    # Montar response com dados extras
    orders_response = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at,
            "user_name": order.user.name if order.user else None,
            "user_email": order.user.email if order.user else None,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "product_name": item.product.name if item.product else None,
                }
                for item in order.items
            ],
        }
        orders_response.append(order_dict)

    return PaginatedResponse(
        data=orders_response,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{order_id}", response_model=SuccessResponse[OrderResponse])
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Buscar pedido por ID."""

    # Se não for admin, passa user_id para filtrar
    current_user_filter = (
        None if current_user.role == UserRole.ADMIN else current_user.id
    )

    order = await OrderService.get_order_by_id(db, order_id, current_user_filter)

    # Montar response
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at,
        "user_name": order.user.name if order.user else None,
        "user_email": order.user.email if order.user else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "product_name": item.product.name if item.product else None,
            }
            for item in order.items
        ],
    }

    return SuccessResponse(data=order_dict, message="Order retrieved successfully")


@router.post("", response_model=SuccessResponse[OrderResponse])
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Criar pedido (usuário cria para si mesmo)."""

    order = await OrderService.create_order(db, order_in, current_user.id)

    # Montar response
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at,
        "user_name": order.user.name if order.user else None,
        "user_email": order.user.email if order.user else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "product_name": item.product.name if item.product else None,
            }
            for item in order.items
        ],
    }

    return SuccessResponse(data=order_dict, message="Order created successfully")


@router.patch("/{order_id}/status", response_model=SuccessResponse[OrderResponse])
async def update_order_status(
    order_id: int,
    status_in: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Atualizar status do pedido (apenas admin)."""

    order = await OrderService.update_order_status(db, order_id, status_in)

    # Montar response
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at,
        "user_name": order.user.name if order.user else None,
        "user_email": order.user.email if order.user else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "product_name": item.product.name if item.product else None,
            }
            for item in order.items
        ],
    }

    return SuccessResponse(data=order_dict, message="Order status updated successfully")


@router.delete("/{order_id}", response_model=SuccessResponse[OrderResponse])
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancelar pedido (usuário cancela próprio pedido)."""

    order = await OrderService.cancel_order(db, order_id, current_user.id)

    # Montar response
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at,
        "user_name": order.user.name if order.user else None,
        "user_email": order.user.email if order.user else None,
        "items": [],
    }

    return SuccessResponse(data=order_dict, message="Order canceled successfully")
