from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Role, User
from backend.decorators import check_role
from backend.models.auth import RegisterItem, RegisterUserResponse
from backend.models.error import BadRequest, Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

register_router = APIRouter(prefix="/register")


@register_router.post("/", response_model=RegisterUserResponse)
@check_role(Permission.CAN_ADMINISTER)
async def register(
    item: RegisterItem, token: TokenJwt = Depends(validate_token)
):
    """
    Register a new user.
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=item.role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if role.can_administer:
            raise BadRequest(code=ErrorCodes.CANNOT_CREATE_ADMIN_USER)

        try:
            ph = Session.password_hasher

            user = User(
                username=item.username,
                password=ph.hash(item.password),
                role=role,
            )

            await user.save(using_db=connection)
        except IntegrityError:
            raise Conflict(code=ErrorCodes.USER_ALREADY_EXISTS)

    return RegisterUserResponse(user=await user.to_dict())
