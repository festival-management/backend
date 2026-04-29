from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Role, RoleTable, Table
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.roles import (
    AddRoleTableResponse,
    AddRoleTableItem,
    RoleTable as RoleTableModel,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_role_table_router = APIRouter()


@add_role_table_router.post(
    "/{role_id}/table", response_model=AddRoleTableResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_role_table(
    role_id: int,
    item: AddRoleTableItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add role table.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        table = await Table.get_or_none(id=item.table_id, using_db=connection)

        if not table:
            raise NotFound(code=ErrorCodes.TABLE_NOT_FOUND)

        new_role_table = RoleTable(
            role=role,
            table=table,
        )

        try:
            await new_role_table.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.ROLE_TABLE_ALREADY_EXISTS)

    return AddRoleTableResponse(
        table=RoleTableModel(**await new_role_table.to_dict())
    )
