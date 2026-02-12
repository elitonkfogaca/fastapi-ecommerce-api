from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.products import Product
from app.models.user import User
from app.schemas.orders import OrderCreate, OrderUpdateStatus, OrderFilter
from app.enums.order_status import OrderStatus


class OrderService:
    """Service para lógica de negócio de pedidos."""

    @staticmethod
    async def get_orders(
        db: AsyncSession, filters: OrderFilter, current_user_id: int | None = None
    ) -> tuple[list[Order], int]:
        """Buscar pedidos com filtros e paginação."""

        # Base query com joins
        query = select(Order).options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product),
        )

        # Aplicar filtros
        conditions = []

        if filters.status:
            conditions.append(Order.status == filters.status)

        if filters.user_id:
            conditions.append(Order.user_id == filters.user_id)

        # Se não for admin, só vê seus próprios pedidos
        if current_user_id and not filters.user_id:
            conditions.append(Order.user_id == current_user_id)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(Order.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = len(total_result.all())

        # Paginação
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Ordenar por data (mais recente primeiro)
        query = query.order_by(Order.created_at.desc())

        result = await db.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    @staticmethod
    async def get_order_by_id(
        db: AsyncSession, order_id: int, current_user_id: int | None = None
    ) -> Order:
        """Buscar pedido por ID."""
        query = (
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).selectinload(OrderItem.product),
            )
            .where(Order.id == order_id)
        )

        # Se não for admin, só vê seu próprio pedido
        if current_user_id:
            query = query.where(Order.user_id == current_user_id)

        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        return order

    @staticmethod
    async def create_order(
        db: AsyncSession, order_in: OrderCreate, user_id: int
    ) -> Order:
        """Criar novo pedido."""

        # Validar produtos e calcular total
        total_price = 0.0
        order_items_data = []

        for item_in in order_in.items:
            # Buscar produto
            product_query = select(Product).where(Product.id == item_in.product_id)
            product_result = await db.execute(product_query)
            product = product_result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item_in.product_id} not found",
                )

            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} is not available",
                )

            # Validar estoque
            if product.stock < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}",
                )

            # Calcular subtotal
            subtotal = product.price * item_in.quantity
            total_price += subtotal

            # Armazenar dados do item
            order_items_data.append(
                {
                    "product_id": product.id,
                    "quantity": item_in.quantity,
                    "unit_price": product.price,
                }
            )

            # Atualizar estoque
            product.stock -= item_in.quantity

        # Criar pedido
        order = Order(
            user_id=user_id,
            total_price=total_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(order)
        await db.flush()  # Para obter o order.id

        # Criar items do pedido
        for item_data in order_items_data:
            order_item = OrderItem(order_id=order.id, **item_data)
            db.add(order_item)

        await db.commit()
        await db.refresh(order)

        # Carregar relationships
        await db.refresh(order, ["user", "items"])
        for item in order.items:
            await db.refresh(item, ["product"])

        return order

    @staticmethod
    async def update_order_status(
        db: AsyncSession, order_id: int, status_in: OrderUpdateStatus
    ) -> Order:
        """Atualizar status do pedido."""

        # Buscar pedido (admin only, sem filtro de user)
        query = (
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).selectinload(OrderItem.product),
            )
            .where(Order.id == order_id)
        )

        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        # Validar transição de status
        if order.status == OrderStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update status of canceled order",
            )

        if order.status == OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update status of delivered order",
            )

        order.status = status_in.status

        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def cancel_order(db: AsyncSession, order_id: int, user_id: int) -> Order:
        """Cancelar pedido (devolve estoque)."""

        # Buscar pedido
        order = await OrderService.get_order_by_id(db, order_id, user_id)

        # Validar se pode cancelar
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status.value}",
            )

        if order.status == OrderStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already canceled",
            )

        # Devolver estoque
        for item in order.items:
            product_query = select(Product).where(Product.id == item.product_id)
            product_result = await db.execute(product_query)
            product = product_result.scalar_one_or_none()

            if product:
                product.stock += item.quantity

        # Atualizar status
        order.status = OrderStatus.CANCELED

        await db.commit()
        await db.refresh(order)

        return order
