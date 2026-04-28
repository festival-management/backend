from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_table_router = APIRouter()


@delete_table_router.delete("/{table_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_table(
    table_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a table from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        table = await Table.get_or_none(id=table_id, using_db=connection)

        if not table:
            raise NotFound(code=ErrorCodes.TABLE_NOT_FOUND)

        await table.delete(using_db=connection)

    return BaseResponse()
