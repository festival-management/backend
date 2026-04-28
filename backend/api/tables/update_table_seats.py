from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.tables import UpdateTableSeatsItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_table_seats_router = APIRouter()


@update_table_seats_router.put(
    "/{table_id}/seats", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_table_seats(
    table_id: int,
    item: UpdateTableSeatsItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update seats of table.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        table = await Table.get_or_none(id=table_id, using_db=connection)

        if not table:
            raise NotFound(code=ErrorCodes.TABLE_NOT_FOUND)

        table.seat_start = item.seat_start
        table.seat_end = item.seat_end

        await table.save(using_db=connection)

    return BaseResponse()
