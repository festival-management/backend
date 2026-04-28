__all__ = (
    "api",
    "auth",
    "menus",
    "orders",
    "printers",
    "products",
    "roles",
    "settings",
    "statistics",
    "subcategories",
    "tables",
    "users",
)

from fastapi import APIRouter

from .auth import auth
from .menus import menus
from .orders import orders
from .printers import printers
from .products import products
from .roles import roles
from .settings import settings
from .statistics import statistics
from .subcategories import subcategories
from .tables import tables
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(menus)
api.include_router(orders)
api.include_router(printers)
api.include_router(products)
api.include_router(roles)
api.include_router(settings)
api.include_router(statistics)
api.include_router(subcategories)
api.include_router(tables)
api.include_router(users)
