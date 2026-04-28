from tortoise import fields
from tortoise.models import Model


class RoleTable(Model):
    """
    The RoleTable model
    """

    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField("models.Role", "tables")
    table = fields.ForeignKeyField("models.Table")

    role_id: int
    table_id: int

    class Meta:
        table = "role_table"
        unique_together = ("role_id", "table_id")

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role_id": self.role_id,
            "table_id": self.table_id,
        }
