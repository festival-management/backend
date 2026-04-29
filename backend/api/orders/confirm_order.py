import datetime
import pytz

from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Unauthorized, NotFound
from backend.models.orders import ConfirmOrderItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.order_utils import is_table_allowed_for_role

confirm_order_router = APIRouter()


@confirm_order_router.patch("/{order_id}/confirm", response_model=BaseResponse)
@check_role(Permission.CAN_CONFIRM_ORDERS)
async def confirm_order(
    order_id: int,
    item: ConfirmOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    if (
        not Session.settings.order_requires_confirmation
        or not token.permissions["can_confirm_orders"]
    ):
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    async with in_transaction() as connection:
        order = (
            await Order.filter(id=order_id)
            .prefetch_related("user__role")
            .using_db(connection)
            .first()
        )

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        if order.is_confirm:
            raise Unauthorized(code=ErrorCodes.ORDER_ALREADY_CONFIRMED)

        if order.user.role.order_confirmer_id != token.role_id:
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        if not await is_table_allowed_for_role(
            token.role_id, item.table, connection
        ):
            raise Unauthorized(code=ErrorCodes.TABLE_NOT_ALLOWED_FOR_ROLE)

        rome_tz = pytz.timezone("Europe/Rome")
        now_in_rome = datetime.datetime.now(rome_tz)

        await order.update_from_dict(
            {
                "table": item.table if not order.is_take_away else None,
                "confirmed_by_id": token.user_id,
                "is_confirm": True,
                "confirmed_at": now_in_rome,
            }
        ).save(using_db=connection)

    return BaseResponse()
