from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subcategories import UpdateSubcategoryNameItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_subcategory_name_router = APIRouter()


@update_subcategory_name_router.put(
    "/{subcategory_id}/name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subcategory_name(
    subcategory_id: int,
    item: UpdateSubcategoryNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of subcategory.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subcategory = await Subcategory.get_or_none(
            id=subcategory_id, using_db=connection
        )

        if not subcategory:
            raise NotFound(code=ErrorCodes.SUBCATEGORY_NOT_FOUND)

        subcategory.name = item.name

        try:
            await subcategory.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBCATEGORY_ALREADY_EXISTS)

    return BaseResponse()
