__all__ = (
    "roles",
    "add_role_printer_router",
    "add_role_table_router",
    "create_role_router",
    "delete_role_router",
    "delete_role_printer_router",
    "delete_role_table_router",
    "get_role_router",
    "get_roles_router",
    "update_role_permissions_router",
    "update_role_name_router",
    "update_role_order_confirmer_router",
)

from fastapi import APIRouter

from .add_role_printer import add_role_printer_router
from .add_role_table import add_role_table_router
from .create_role import create_role_router
from .delete_role import delete_role_router
from .delete_role_printer import delete_role_printer_router
from .delete_role_table import delete_role_table_router
from .get_role import get_role_router
from .get_roles import get_roles_router
from .udpate_role_permissions import update_role_permissions_router
from .update_role_name import update_role_name_router
from .update_role_order_confirmer import update_role_order_confirmer_router

roles = APIRouter(prefix="/roles", tags=["roles"])
roles.include_router(add_role_printer_router)
roles.include_router(add_role_table_router)
roles.include_router(create_role_router)
roles.include_router(delete_role_router)
roles.include_router(delete_role_printer_router)
roles.include_router(delete_role_table_router)
roles.include_router(get_role_router)
roles.include_router(get_roles_router)
roles.include_router(update_role_permissions_router)
roles.include_router(update_role_name_router)
roles.include_router(update_role_order_confirmer_router)
