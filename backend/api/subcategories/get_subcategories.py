from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError

from backend.config import Session
from backend.database.models import Subcategory
from backend.models.error import NotFound
from backend.models.subcategories import (
    GetSubcategoriesResponse,
    Subcategory as SubcategoryModel,
    SubcategoryName,
)
from backend.utils import TokenJwt, validate_token, ErrorCodes

get_subcategories_router = APIRouter()


@get_subcategories_router.get("/", response_model=GetSubcategoriesResponse)
async def get_subcategories(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of subcategories.

    **Permission**: can_administer
    """

    subcategories_query = Subcategory.all()

    if order_by:
        try:
            subcategories_query = subcategories_query.order_by(order_by)
        except FieldError:
            raise NotFound(code=ErrorCodes.UNKNOWN_ORDER_BY_PARAMETER)

    total_count = await subcategories_query.count()

    if not limit:
        limit = (
            total_count - offset
            if only_name
            else Session.config.DEFAULT_LIMIT_VALUE
        )

    subcategories = await subcategories_query.offset(offset).limit(limit)

    return GetSubcategoriesResponse(
        total_count=total_count,
        subcategories=[
            SubcategoryName(**await subcategory.to_dict_name())
            if only_name
            else SubcategoryModel(**await subcategory.to_dict())
            for subcategory in subcategories
        ],
    )
