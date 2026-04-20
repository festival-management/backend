from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import User
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.users import UpdateUserPasswordItem
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.enums import Permission

update_user_password_router = APIRouter()


@update_user_password_router.put(
    "/{user_id}/password", response_model=BaseResponse
)
async def update_user_password(
    user_id: int,
    item: UpdateUserPasswordItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update password of user.
    """

    async with in_transaction() as connection:
        user = await User.get_or_none(id=user_id, using_db=connection)

        if not user:
            raise NotFound(code=ErrorCodes.USER_NOT_FOUND)

        if not (
            token.permissions.get(Permission.CAN_ADMINISTER, False)
            or token.user_id == user.id
        ):
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        ph = Session.password_hasher
        user.password = ph.hash(item.password)

        try:
            await user.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.USER_ALREADY_EXISTS)

    return BaseResponse()
