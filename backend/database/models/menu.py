import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import MenuDate, MenuField, MenuRole


class Menu(Model):
    """
    The Menu model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    short_name = fields.CharField(20, unique=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    daily_max_sales = fields.IntField(null=True)

    dates: fields.ReverseRelation["MenuDate"]
    menu_fields: fields.ReverseRelation["MenuField"]
    roles: fields.ReverseRelation["MenuRole"]

    class Meta:
        table = "menu"

    async def to_dict(
        self,
        include_dates: bool = False,
        include_fields: bool = False,
        include_fields_products: bool = False,
        include_fields_products_dates: bool = False,
        include_fields_products_ingredients: bool = False,
        include_fields_products_roles: bool = False,
        include_fields_products_variants: bool = False,
        include_roles: bool = False,
    ) -> dict:
        # Build the base result
        result = {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "price": self.price,
            "daily_max_sales": self.daily_max_sales,
        }

        # Add dates if pre-fetched and requested
        if include_dates and hasattr(self, "dates"):
            result["dates"] = [await date.to_dict() for date in self.dates]

        # Add fields if pre-fetched and requested
        if include_fields and hasattr(self, "menu_fields"):
            result["fields"] = [
                await field.to_dict(
                    include_fields_products,
                    include_fields_products_dates,
                    include_fields_products_ingredients,
                    include_fields_products_roles,
                    include_fields_products_variants,
                )
                for field in self.menu_fields
            ]

        # Add roles if pre-fetched and requested
        if include_roles and hasattr(self, "roles"):
            result["roles"] = [await role.to_dict() for role in self.roles]

        return result
