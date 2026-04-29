from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import BadRequest, Conflict, NotFound, Unauthorized
from backend.models.orders import (
    CreateOrderItem,
    CreateOrderResponse,
    Order as OrderModel,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.order_utils import (
    check_menus,
    check_products,
    create_order_menus,
    create_order_products,
    get_order_price,
    is_table_allowed_for_role,
)

create_order_router = APIRouter()


@create_order_router.post("/", response_model=CreateOrderResponse)
@check_role(Permission.CAN_ORDER)
async def create_order(
    item: CreateOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new order.

    **Permission**: can_order
    """

    if not item.products and not item.menus:
        raise BadRequest(code=ErrorCodes.NO_PRODUCTS_AND_MENUS)

    if (
        not item.is_take_away
        and not Session.settings.order_requires_confirmation
        and not item.guests
        and not item.table
        and not item.parent_order_id
    ):
        raise BadRequest(code=ErrorCodes.SET_GUESTS_NUMBER)

    if (
        not item.is_take_away
        and Session.settings.order_requires_confirmation
        and not item.guests
        and not item.parent_order_id
    ):
        raise BadRequest(code=ErrorCodes.SET_GUESTS_NUMBER)

    async with in_transaction() as connection:
        await connection.execute_query(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        )

        if item.parent_order_id:
            parent_order = await Order.get_or_none(
                id=item.parent_order_id, using_db=connection
            )

            if not parent_order:
                raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        if (
            not Session.settings.order_requires_confirmation
            and not await is_table_allowed_for_role(
                token.role_id, item.table, connection
            )
        ):
            raise Unauthorized(code=ErrorCodes.TABLE_NOT_ALLOWED_FOR_ROLE)

        has_error_products, error_code_products = await check_products(
            item.products, token.role_id, connection
        )

        if has_error_products:
            raise Conflict(code=error_code_products)

        has_error_menus, error_code_menus = await check_menus(
            item.menus, token.role_id, connection
        )

        if has_error_menus:
            raise Conflict(code=error_code_menus)

        order_price = await get_order_price(item)

        order = await Order.create(
            customer=item.customer,
            guests=(
                item.guests
                if not item.is_take_away and not item.parent_order_id
                else None
            ),
            is_take_away=(
                item.is_take_away if not item.parent_order_id else False
            ),
            table=(
                item.table
                if not item.is_take_away
                and not Session.settings.order_requires_confirmation
                and not item.parent_order_id
                else None
            ),
            is_confirm=(
                True
                if not Session.settings.order_requires_confirmation
                else False
            ),
            is_voucher=item.is_voucher,
            price=order_price,
            user_id=token.user_id,
            parent_order_id=item.parent_order_id,
            using_db=connection,
        )

        await create_order_products(item.products, order, connection)
        await create_order_menus(item.menus, order, connection)

    return CreateOrderResponse(order=OrderModel(**await order.to_dict()))
