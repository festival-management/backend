from tortoise import fields
from tortoise.models import Model


class ProductIngredient(Model):
    """
    The ProductIngredient model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = fields.BooleanField(default=False)
    product = fields.ForeignKeyField("models.Product", "ingredients")

    product_id: int

    class Meta:
        table = "product_ingredient"
        unique_together = ("name", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "product_id": self.product_id,
        }
