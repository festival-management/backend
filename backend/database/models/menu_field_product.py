from tortoise import fields
from tortoise.models import Model


class MenuFieldProduct(Model):
    """
    The MenuFieldProduct model
    """

    id = fields.IntField(pk=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    product = fields.ForeignKeyField("models.Product")
    menu_field = fields.ForeignKeyField("models.MenuField", "field_products")

    product_id: int
    menu_field_id: int

    class Meta:
        table = "menu_field_product"
        unique_together = ("product_id", "menu_field_id")

    async def to_dict(
        self,
        include_fields_products_dates: bool = False,
        include_fields_products_ingredients: bool = False,
        include_fields_products_roles: bool = False,
        include_fields_products_variants: bool = False,
    ):
        return {
            "id": self.id,
            "price": self.price,
            "product": await self.product.to_dict(
                include_fields_products_dates,
                include_fields_products_ingredients,
                include_fields_products_roles,
                include_fields_products_variants,
            ),
            "menu_field_id": self.menu_field_id,
        }
