from decimal import Decimal

from pydantic import BaseModel

from backend.models import BaseResponse


class StatisticProduct(BaseModel):
    name: str
    quantity: int
    pending_quantity: int
    price: Decimal
    total_price: Decimal


class Statistic(BaseModel):
    total_orders: int
    total_seated: int
    total_take_away: int
    total_voucher: int
    total_price_with_cover: Decimal
    total_price_without_cover: Decimal
    products: list[StatisticProduct]


class GetStatisticResponse(BaseResponse, Statistic):
    pass
