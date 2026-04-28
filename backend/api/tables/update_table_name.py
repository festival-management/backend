from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.tables import UpdateTableNameItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_table_name_router = APIRouter()


@update_table_name_router.put("/{table_id}/name", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_table_name(
    table_id: int,
    item: UpdateTableNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of table.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        table = await Table.get_or_none(id=table_id, using_db=connection)

        if not table:
            raise NotFound(code=ErrorCodes.TABLE_NOT_FOUND)

        table.name = item.name

        try:
            await table.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.TABLE_ALREADY_EXISTS)

    return BaseResponse()
