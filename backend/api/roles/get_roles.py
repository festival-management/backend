from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.roles import GetRolesResponse, Role as RoleModel, RoleName
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination

get_roles_router = APIRouter()


@get_roles_router.get("/", response_model=GetRolesResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_roles(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    can_order: bool | None = None,
    include_printers: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of roles.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        query = ~Q(id=token.role_id)

        if can_order is not None:
            query &= Q(can_order=can_order)

        roles_query, total_count, limit = await process_query_with_pagination(
            Role, query, connection, offset, limit, ""
        )

        try:
            roles = (
                await roles_query.prefetch_related("printers")
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetRolesResponse(
        total_count=total_count,
        roles=[
            RoleName(**await role.to_dict_name())
            if only_name
            else RoleModel(**await role.to_dict(include_printers))
            for role in roles
        ],
    )
