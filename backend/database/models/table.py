from tortoise import fields
from tortoise.models import Model


class Table(Model):
    """
    The Table model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    seat_start = fields.IntField()
    seat_end = fields.IntField()

    class Meta:
        table = "table"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "seat_start": self.seat_start,
            "seat_end": self.seat_end,
        }
