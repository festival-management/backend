from pydantic import BaseModel, field_validator, Field, model_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, check_seat_range


class Table(BaseModel):
    id: int
    name: str
    seat_start: int
    seat_end: int


class TableName(BaseModel):
    id: int
    name: str


class CreateTableItem(BaseModel):
    name: str
    seat_start: int = Field(ge=1)
    seat_end: int = Field(ge=1)

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @model_validator(mode="after")
    def check_seat_range(self):
        check_seat_range(self.seat_start, self.seat_end)

        return self


class CreateTableResponse(BaseResponse):
    table: Table


class GetTableResponse(BaseResponse, Table):
    pass


class GetTablesResponse(BaseResponse):
    total_count: int
    tables: list[Table | TableName]


class UpdateTableNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateTableSeatsItem(BaseModel):
    seat_start: int
    seat_end: int

    @model_validator(mode="after")
    def check_seat_range(self):
        check_seat_range(self.seat_start, self.seat_end)

        return self
