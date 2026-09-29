import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.models.models import MachineField
from app.routers import fields, machines


app = FastAPI(
    title="Dynamic Machine Risk API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


INITIAL_FIELDS = [
    {
        "key": "machine_name",
        "name": "Machine Name",
        "field_type": "text",
        "required": True,
        "options": None,
    },
    {
        "key": "temperature",
        "name": "Temperature",
        "field_type": "number",
        "required": True,
        "options": None,
    },
    {
        "key": "pressure",
        "name": "Pressure",
        "field_type": "number",
        "required": True,
        "options": None,
    },
    {
        "key": "vibration",
        "name": "Vibration",
        "field_type": "dropdown",
        "required": True,
        "options": ["Low", "Medium", "High"],
    },
]


def seed_initial_fields():
    db = SessionLocal()

    try:
        for field_data in INITIAL_FIELDS:
            existing = (
                db.query(MachineField)
                .filter(
                    MachineField.key == field_data["key"]
                )
                .first()
            )

            if existing:
                continue

            db.add(
                MachineField(
                    key=field_data["key"],
                    name=field_data["name"],
                    field_type=field_data["field_type"],
                    required=field_data["required"],
                    options=(
                        json.dumps(field_data["options"])
                        if field_data["options"]
                        else None
                    ),
                )
            )

        db.commit()

    finally:
        db.close()


seed_initial_fields()


app.include_router(fields.router)
app.include_router(machines.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "machine-risk-api",
    }