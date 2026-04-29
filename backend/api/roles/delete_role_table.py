from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Role, RoleTable
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_role_table_router = APIRouter()


@delete_role_table_router.delete(
    "/{role_id}/table/{role_table_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_role_table(
    role_id: int,
    role_table_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a role table from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        role_table = await RoleTable.get_or_none(
            id=role_table_id, role=role, using_db=connection
        )

        if not role_table:
            raise NotFound(code=ErrorCodes.ROLE_TABLE_NOT_FOUND)

        await role_table.delete(using_db=connection)

    return BaseResponse()
