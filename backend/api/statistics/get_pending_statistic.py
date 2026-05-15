from collections import defaultdict

from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import UnprocessableEntity
from backend.models.statistics import (
    GetPendingStatisticResponse,
    PendingStatisticProduct,
)
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes
from backend.utils.costants import ROLE_ID_REGEX
from backend.utils.datetime_utils import get_day_bounds

get_pending_statistic_router = APIRouter()


@get_pending_statistic_router.get(
    "/pending", response_model=GetPendingStatisticResponse
)
@check_role(Permission.CAN_STATISTICS, Permission.CAN_PRIORITY_STATISTICS)
async def get_pending_statistic(
    role_ids: str | None = None,
    only_confirmed_order: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get pending statistic.

    **Permission**: can_statistics || can_priority_statistics
    """

    query_filters = Q()
    can_priority_statistics = token.permissions["can_priority_statistics"]

    start_date, end_date = get_day_bounds()
    query_filters &= Q(created_at__gt=start_date)
    query_filters &= Q(created_at__lt=end_date)

    if only_confirmed_order:
        query_filters &= Q(is_confirm=True)
    if role_ids:
        if not ROLE_ID_REGEX.fullmatch(role_ids):
            raise UnprocessableEntity(code=ErrorCodes.REQUEST_VALIDATION_ERROR)

        role_ids = list(map(int, role_ids.split(",")))
        query_filters &= Q(user__role_id__in=role_ids)

    async with in_transaction() as connection:
        orders = (
            await Order.filter(query_filters, is_deleted=False)
            .prefetch_related("order_products__product", "order_menus__menu")
            .using_db(connection)
        )

        total_take_away = sum(1 for order in orders if order.is_take_away)
        total_seated = sum(
            order.guests or 0 for order in orders if not order.is_take_away
        )

        result_map: dict[str, int] = defaultdict(int)

        for order in orders:
            order_products = [
                (op, op.product.name)
                for op in order.order_products
                if op.order_menu_field_id is None
                and (not can_priority_statistics or op.product.is_priority)
            ]
            order_menus = [
                (om, om.menu.name)
                for om in order.order_menus
                if not can_priority_statistics
            ]

            for x, name in order_products + order_menus:
                if not result_map.get(name):
                    result_map[name] = 0

                if not order.is_served:
                    result_map[name] += x.quantity

        result = [
            PendingStatisticProduct(
                name=name,
                pending_quantity=pending_quantity,
            )
            for name, pending_quantity in result_map.items()
        ]

    return GetPendingStatisticResponse(
        total_orders=len(orders),
        total_seated=total_seated,
        total_take_away=total_take_away,
        products=result,
    )
