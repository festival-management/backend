from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Unauthorized, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

serve_order_router = APIRouter()


@serve_order_router.patch("/{order_id}/serve", response_model=BaseResponse)
@check_role(Permission.CAN_SERVE_ORDERS)
async def serve_order(
    order_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Serve an order.

    **Permission**: can_serve_orders
    """

    async with in_transaction() as connection:
        order = await Order.filter(id=order_id).using_db(connection).first()

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        if order.is_served:
            raise Unauthorized(code=ErrorCodes.ORDER_ALREADY_SERVED)

        if not order.is_done or order.is_deleted:
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        order.is_served = True

        await order.save(using_db=connection)

    return BaseResponse()
