from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.menu import CreateMenuItem, CreateMenuResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_menu_router = APIRouter()


@create_menu_router.post("/", response_model=CreateMenuResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_menu(
    item: CreateMenuItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new menu.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_menu = Menu(
            name=item.name, short_name=item.short_name, price=item.price
        )

        try:
            await new_menu.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_ALREADY_EXISTS)

    return CreateMenuResponse(menu=await new_menu.to_dict())
