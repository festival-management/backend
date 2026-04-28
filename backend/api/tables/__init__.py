__all__ = (
    "tables",
    "create_table_router",
    "delete_table_router",
    "get_table_router",
    "get_tables_router",
    "update_table_name_router",
    "update_table_seats_router",
)

from fastapi import APIRouter

from .create_table import create_table_router
from .delete_table import delete_table_router
from .get_table import get_table_router
from .get_tables import get_tables_router
from .update_table_name import update_table_name_router
from .update_table_seats import update_table_seats_router

tables = APIRouter(prefix="/tables", tags=["tables"])
tables.include_router(create_table_router)
tables.include_router(delete_table_router)
tables.include_router(get_table_router)
tables.include_router(get_tables_router)
tables.include_router(update_table_name_router)
tables.include_router(update_table_seats_router)
