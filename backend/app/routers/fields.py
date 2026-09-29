import json
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import MachineField
from app.schemas.field import FieldCreate, FieldResponse, FieldUpdate


router = APIRouter(
    prefix="/fields",
    tags=["Fields"],
)


def make_key(name: str) -> str:
    key = name.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")

    if not key:
        raise HTTPException(
            status_code=400,
            detail="Field name must contain letters or numbers.",
        )

    return key


def validate_field_data(
    field_type: str,
    options: list[str] | None,
) -> list[str] | None:

    if field_type == "dropdown":
        if not options:
            raise HTTPException(
                status_code=400,
                detail="Dropdown fields must contain at least one option.",
            )

        cleaned_options = [
            option.strip()
            for option in options
            if option.strip()
        ]

        if not cleaned_options:
            raise HTTPException(
                status_code=400,
                detail="Dropdown fields must contain at least one valid option.",
            )

        return cleaned_options

    return None


def field_to_response(field: MachineField) -> FieldResponse:
    options = None

    if field.options:
        options = json.loads(field.options)

    return FieldResponse(
        id=field.id,
        key=field.key,
        name=field.name,
        field_type=field.field_type,
        required=field.required,
        options=options,
    )


@router.get("", response_model=list[FieldResponse])
def get_fields(db: Session = Depends(get_db)):
    fields = (
        db.query(MachineField)
        .order_by(MachineField.id)
        .all()
    )

    return [
        field_to_response(field)
        for field in fields
    ]


@router.post(
    "",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_field(
    payload: FieldCreate,
    db: Session = Depends(get_db),
):
    name = payload.name.strip()
    key = make_key(name)

    existing_name = (
        db.query(MachineField)
        .filter(MachineField.name == name)
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="A field with this name already exists.",
        )

    existing_key = (
        db.query(MachineField)
        .filter(MachineField.key == key)
        .first()
    )

    if existing_key:
        raise HTTPException(
            status_code=400,
            detail="A field with this key already exists.",
        )

    options = validate_field_data(
        payload.field_type,
        payload.options,
    )

    field = MachineField(
        key=key,
        name=name,
        field_type=payload.field_type,
        required=payload.required,
        options=json.dumps(options) if options else None,
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    return field_to_response(field)


@router.put(
    "/{field_id}",
    response_model=FieldResponse,
)
def update_field(
    field_id: int,
    payload: FieldUpdate,
    db: Session = Depends(get_db),
):
    field = (
        db.query(MachineField)
        .filter(MachineField.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found.",
        )

    name = payload.name.strip()

    duplicate_name = (
        db.query(MachineField)
        .filter(
            MachineField.name == name,
            MachineField.id != field_id,
        )
        .first()
    )

    if duplicate_name:
        raise HTTPException(
            status_code=400,
            detail="A field with this name already exists.",
        )

    options = validate_field_data(
        payload.field_type,
        payload.options,
    )

    field.name = name
    field.field_type = payload.field_type
    field.required = payload.required
    field.options = (
        json.dumps(options)
        if options
        else None
    )

    # field.key deliberately remains unchanged so it is a stable
    # machine-readable identifier even if the display name changes.

    db.commit()
    db.refresh(field)

    return field_to_response(field)


@router.delete("/{field_id}")
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
):
    field = (
        db.query(MachineField)
        .filter(MachineField.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found.",
        )

    db.delete(field)
    db.commit()

    return {
        "message": "Field deleted successfully."
    }