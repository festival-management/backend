import typing

from tortoise import fields
from tortoise.models import Model

from backend.utils import ErrorCodes

if typing.TYPE_CHECKING:
    from backend.database.models import RolePrinter


class Role(Model):
    """
    The Role model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    can_administer = fields.BooleanField(default=False)
    can_order = fields.BooleanField(default=False)
    can_statistics = fields.BooleanField(default=False)
    can_priority_statistics = fields.BooleanField(default=False)
    can_confirm_orders = fields.BooleanField(default=False)

    printers: fields.ReverseRelation["RolePrinter"]

    class Meta:
        table = "role"

    async def save(self, *args, **kwargs):
        if self.can_statistics and self.can_priority_statistics:
            raise ValueError(ErrorCodes.ONLY_ONE_STATISTICS_CAN_BE_TRUE)

        await super().save(*args, **kwargs)

    async def get_permissions(self) -> dict:
        return {
            "can_administer": self.can_administer,
            "can_order": self.can_order,
            "can_statistics": self.can_statistics,
            "can_priority_statistics": self.can_priority_statistics,
            "can_confirm_orders": self.can_confirm_orders,
        }

    async def to_dict_name(self) -> dict:
        return {"id": self.id, "name": self.name}

    async def to_dict(self, include_printers: bool = False) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "permissions": await self.get_permissions(),
        }

        # Add printers if pre-fetched and requested
        if include_printers and hasattr(self, "printers"):
            result["printers"] = [
                await printer.to_dict() for printer in self.printers
            ]

        return result
