from fastapi import APIRouter, Depends

from backend.database.models import Role, User
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import BadRequest, NotFound, Unauthorized
from backend.models.users import UpdateUserRoleItem
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.enums import Permission

update_user_role_router = APIRouter()


@update_user_role_router.put("/{user_id}/role", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_user_name(
    user_id: int,
    item: UpdateUserRoleItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update role of user.

    **Permission**: can_administer
    """

    user = await User.get_or_none(id=user_id)

    if not user:
        raise NotFound(code=ErrorCodes.USER_NOT_FOUND)

    if user.username == "admin":
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    role = await Role.get_or_none(id=item.role_id)

    if not role:
        raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    if role.can_administer:
        raise BadRequest(code=ErrorCodes.NOT_ALLOWED)

    user.role = role

    await user.save()

    return BaseResponse()
