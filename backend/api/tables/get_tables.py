from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.tables import (
    GetTablesResponse,
    Table as TableModel,
    TableName,
)
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination

get_tables_router = APIRouter()


@get_tables_router.get("/", response_model=GetTablesResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_tables(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of tables.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        (
            table_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Table, Q(), connection, offset, limit, order_by
        )

        try:
            tables = await table_query.offset(offset).limit(limit)
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetTablesResponse(
        total_count=total_count,
        tables=[
            (
                TableName(**await table.to_dict_name())
                if only_name
                else TableModel(**await table.to_dict())
            )
            for table in tables
        ],
    )
