from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.tables import GetTableResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_table_router = APIRouter()


@get_table_router.get("/{table_id}", response_model=GetTableResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_table(table_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Get information about a table.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        table = await Table.get_or_none(id=table_id, using_db=connection)

        if not table:
            raise NotFound(code=ErrorCodes.TABLE_NOT_FOUND)

    return GetTableResponse(**await table.to_dict())
