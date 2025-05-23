import datetime

from fastapi import APIRouter, Depends
from tortoise.functions import Sum
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Order, OrderProduct, OrderMenu
from backend.decorators import check_role
from backend.models.statistics import GetStatisticResponse, StatisticProduct
from backend.utils import Permission, TokenJwt, validate_token

get_statistic_router = APIRouter()


@get_statistic_router.get("/", response_model=GetStatisticResponse)
@check_role(Permission.CAN_STATISTICS, Permission.CAN_PRIORITY_STATISTICS)
async def get_statistic(
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get statistic.

    **Permission**: can_statistics || can_priority_statistics
    """

    query_filters = Q()
    can_priority_statistics = token.permissions["can_priority_statistics"]

    if start_date:
        query_filters &= Q(created_at__gt=start_date)
    if end_date:
        query_filters &= Q(created_at__lt=end_date)

    async with in_transaction() as connection:
        orders = (
            await Order.filter(query_filters)
            .using_db(connection)
            .values("id", "guests", "is_take_away")
        )
        order_ids = list(map(lambda x: x["id"], orders))

        total_take_away = 0
        total_seated = 0

        for order in orders:
            if order["is_take_away"]:
                total_take_away += 1
            else:
                total_seated += order["guests"]

        order_products_filters = Q(order_menu_field_id=None) & Q(
            order_id__in=order_ids
        )

        if can_priority_statistics:
            order_products_filters &= Q(product__is_priority=True)

        order_products = (
            await OrderProduct.filter(order_products_filters)
            .using_db(connection)
            .annotate(total_quantity=Sum("quantity"), total_price=Sum("price"))
            .group_by("product__name")
            .values("product__name", "total_quantity", "total_price")
        )
        order_menus = (
            await OrderMenu.filter(Q(order_id__in=order_ids))
            .using_db(connection)
            .annotate(total_quantity=Sum("quantity"), total_price=Sum("price"))
            .group_by("menu__name")
            .values("menu__name", "total_quantity", "total_price")
        )

    result = []

    for order_product in order_products:
        result.append(
            StatisticProduct(
                name=order_product["product__name"],
                quantity=order_product["total_quantity"],
                price=order_product["total_price"],
            )
        )

    for order_menu in order_menus if not can_priority_statistics else []:
        result.append(
            StatisticProduct(
                name=order_menu["menu__name"],
                quantity=order_menu["total_quantity"],
                price=order_menu["total_price"],
            )
        )

    return GetStatisticResponse(
        total_orders=len(orders),
        total_seated=total_seated,
        total_take_away=total_take_away,
        products=result,
    )
