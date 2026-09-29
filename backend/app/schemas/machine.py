from typing import Any

from pydantic import BaseModel


class MachineValueInput(BaseModel):
    field_id: int
    value: Any


class MachineCreate(BaseModel):
    values: list[MachineValueInput]


class MachineUpdate(BaseModel):
    values: list[MachineValueInput]


class MachineValueResponse(BaseModel):
    field_id: int
    field_key: str
    field_name: str
    field_type: str
    value: Any


class MachineResponse(BaseModel):
    id: int
    values: list[MachineValueResponse]