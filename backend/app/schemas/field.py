from typing import Literal

from pydantic import BaseModel, Field


FieldType = Literal["text", "number", "dropdown"]


class FieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    field_type: FieldType
    required: bool = False
    options: list[str] | None = None


class FieldUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    field_type: FieldType
    required: bool = False
    options: list[str] | None = None


class FieldResponse(BaseModel):
    id: int
    key: str
    name: str
    field_type: str
    required: bool
    options: list[str] | None