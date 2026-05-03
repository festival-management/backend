__all__ = (
    "orders",
    "create_order_router",
    "delete_order_router",
    "get_order_router",
    "get_orders_router",
    "print_order_router",
    "serve_order_router",
)

from fastapi import APIRouter

from .confirm_order import confirm_order_router
from .create_order import create_order_router
from .delete_order import delete_order_router
from .get_order import get_order_router
from .get_orders import get_orders_router
from .print_order import print_order_router
from .serve_order import serve_order_router

orders = APIRouter(prefix="/orders", tags=["orders"])
orders.include_router(confirm_order_router)
orders.include_router(create_order_router)
orders.include_router(delete_order_router)
orders.include_router(get_order_router)
orders.include_router(get_orders_router)
orders.include_router(print_order_router)
orders.include_router(serve_order_router)
