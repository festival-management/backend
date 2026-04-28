from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Table
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.tables import (
    CreateTableResponse,
    CreateTableItem,
    Table as TableModel,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_table_router = APIRouter()


@create_table_router.post("/", response_model=CreateTableResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_table(
    item: CreateTableItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new table.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_table = Table(
            name=item.name, seat_start=item.seat_start, seat_end=item.seat_end
        )

        try:
            await new_table.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.TABLE_ALREADY_EXISTS)

    return CreateTableResponse(table=TableModel(**await new_table.to_dict()))
