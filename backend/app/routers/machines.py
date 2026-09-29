import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Machine, MachineField, MachineFieldValue
from app.schemas.machine import (
    MachineCreate,
    MachineResponse,
    MachineUpdate,
    MachineValueResponse,
)


router = APIRouter(
    prefix="/machines",
    tags=["Machines"],
)


def convert_value_for_response(
    field_type: str,
    value: str,
) -> Any:
    if field_type == "number":
        try:
            number = float(value)

            if number.is_integer():
                return int(number)

            return number
        except ValueError:
            return value

    return value


def validate_machine_values(
    submitted_values,
    fields: list[MachineField],
):
    field_map = {
        field.id: field
        for field in fields
    }

    submitted_map = {}

    for item in submitted_values:
        if item.field_id in submitted_map:
            raise HTTPException(
                status_code=400,
                detail=f"Field ID {item.field_id} was submitted more than once.",
            )

        field = field_map.get(item.field_id)

        if not field:
            raise HTTPException(
                status_code=400,
                detail=f"Field ID {item.field_id} does not exist.",
            )

        value = item.value

        if value is None or (
            isinstance(value, str)
            and not value.strip()
        ):
            if field.required:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.name} is required.",
                )

            continue

        if field.field_type == "number":
            try:
                float(value)
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.name} must be a number.",
                )

        if field.field_type == "dropdown":
            options = (
                json.loads(field.options)
                if field.options
                else []
            )

            if str(value) not in options:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{field.name} must be one of: "
                        f"{', '.join(options)}."
                    ),
                )

        submitted_map[item.field_id] = str(value)

    for field in fields:
        if field.required and field.id not in submitted_map:
            raise HTTPException(
                status_code=400,
                detail=f"{field.name} is required.",
            )

    return submitted_map


def machine_to_response(machine: Machine) -> MachineResponse:
    ordered_values = sorted(
        machine.values,
        key=lambda item: item.field.id,
    )

    values = [
        MachineValueResponse(
            field_id=value.field.id,
            field_key=value.field.key,
            field_name=value.field.name,
            field_type=value.field.field_type,
            value=convert_value_for_response(
                value.field.field_type,
                value.value,
            ),
        )
        for value in ordered_values
    ]

    return MachineResponse(
        id=machine.id,
        values=values,
    )


def get_machine_or_404(
    machine_id: int,
    db: Session,
):
    machine = (
        db.query(Machine)
        .options(
            joinedload(Machine.values)
            .joinedload(MachineFieldValue.field)
        )
        .filter(Machine.id == machine_id)
        .first()
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    return machine


@router.get(
    "",
    response_model=list[MachineResponse],
)
def get_machines(db: Session = Depends(get_db)):
    machines = (
        db.query(Machine)
        .options(
            joinedload(Machine.values)
            .joinedload(MachineFieldValue.field)
        )
        .order_by(Machine.id)
        .all()
    )

    return [
        machine_to_response(machine)
        for machine in machines
    ]


@router.get(
    "/{machine_id}",
    response_model=MachineResponse,
)
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db),
):
    machine = get_machine_or_404(
        machine_id,
        db,
    )

    return machine_to_response(machine)


@router.post(
    "",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_machine(
    payload: MachineCreate,
    db: Session = Depends(get_db),
):
    fields = (
        db.query(MachineField)
        .order_by(MachineField.id)
        .all()
    )

    if not fields:
        raise HTTPException(
            status_code=400,
            detail="No machine fields are configured.",
        )

    values = validate_machine_values(
        payload.values,
        fields,
    )

    try:
        machine = Machine()
        db.add(machine)
        db.flush()

        for field_id, value in values.items():
            db.add(
                MachineFieldValue(
                    machine_id=machine.id,
                    field_id=field_id,
                    value=value,
                )
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    machine = get_machine_or_404(
        machine.id,
        db,
    )

    return machine_to_response(machine)


@router.put(
    "/{machine_id}",
    response_model=MachineResponse,
)
def update_machine(
    machine_id: int,
    payload: MachineUpdate,
    db: Session = Depends(get_db),
):
    machine = get_machine_or_404(
        machine_id,
        db,
    )

    fields = (
        db.query(MachineField)
        .order_by(MachineField.id)
        .all()
    )

    values = validate_machine_values(
        payload.values,
        fields,
    )

    try:
        existing_values = {
            value.field_id: value
            for value in machine.values
        }

        for field_id, existing_value in list(existing_values.items()):
            if field_id not in values:
                db.delete(existing_value)

        for field_id, value in values.items():
            existing_value = existing_values.get(field_id)

            if existing_value:
                existing_value.value = value
            else:
                db.add(
                    MachineFieldValue(
                        machine_id=machine.id,
                        field_id=field_id,
                        value=value,
                    )
                )

        db.commit()

    except Exception:
        db.rollback()
        raise

    machine = get_machine_or_404(
        machine_id,
        db,
    )

    return machine_to_response(machine)


@router.delete("/{machine_id}")
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
):
    machine = get_machine_or_404(
        machine_id,
        db,
    )

    db.delete(machine)
    db.commit()

    return {
        "message": "Machine deleted successfully."
    }