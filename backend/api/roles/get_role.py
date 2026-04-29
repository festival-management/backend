from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.roles import GetRoleResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_role_router = APIRouter()


@get_role_router.get("/{role_id}", response_model=GetRoleResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_role(
    role_id: int,
    include_order_confirmer: bool = False,
    include_printers: bool = False,
    include_tables: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about a role.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(
            id=role_id, using_db=connection
        ).prefetch_related("printers", "order_confirmer", "tables")

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    return GetRoleResponse(
        **await role.to_dict(
            include_order_confirmer, include_printers, include_tables
        )
    )
