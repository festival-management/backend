from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.utils import (
    Category,
    validate_name_field,
    validate_short_name_field,
)


class Product(BaseModel):
    id: int
    name: str
    short_name: str
    is_priority: bool
    price: float
    category: Category
    subcategory_id: int


class ProductName(BaseModel):
    id: int
    name: str


class CreateProductItem(BaseModel):
    name: str
    short_name: str
    price: float = Field(ge=0)
    category: Category
    subcategory_id: int

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @field_validator("short_name")
    @classmethod
    def validate_short_name_field(cls, short_name: str):
        return validate_short_name_field(short_name)


class CreateProductResponse(BaseResponse):
    product: Product


class GetProductResponse(BaseResponse, Product):
    pass


class GetProductsResponse(BaseResponse):
    total_count: int
    products: list[Product | ProductName]