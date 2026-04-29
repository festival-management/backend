from __future__ import annotations

from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import (
    Permission,
    validate_name_field,
    validate_permissions_field,
    PrinterType,
)


class RolePrinter(BaseModel):
    id: int
    printer_id: int
    printer_type: PrinterType


class RoleTable(BaseModel):
    id: int
    table_id: int


class Role(BaseModel):
    id: int
    name: str
    permissions: dict[Permission, bool]
    order_confirmer: Role | None = None
    printers: list[RolePrinter] | None = None
    tables: list[RoleTable] | None = None


class RoleName(BaseModel):
    id: int
    name: str


class AddRolePrinterItem(BaseModel):
    printer_id: int
    printer_type: PrinterType


class AddRolePrinterResponse(BaseResponse):
    printer: RolePrinter


class AddRoleTableItem(BaseModel):
    table_id: int


class AddRoleTableResponse(BaseResponse):
    table: RoleTable


class CreateRoleItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreateRoleResponse(BaseResponse):
    role: Role


class GetRolesResponse(BaseResponse):
    total_count: int
    roles: list[Role | RoleName]


class GetRoleResponse(BaseResponse, Role):
    pass


class UpdateRoleNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateRolePermissionsItem(BaseModel):
    permissions: dict[Permission, bool]

    @field_validator("permissions")
    @classmethod
    def validate_permissions_field(cls, permissions: dict[Permission, bool]):
        return validate_permissions_field(permissions)


class UpdateRoleOrderConfirmerItem(BaseModel):
    order_confirmer_id: int | None = None
