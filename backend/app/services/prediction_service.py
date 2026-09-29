from pathlib import Path

import joblib
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.models import Machine, MachineFieldValue


MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ml"
    / "risk_model.joblib"
)

MODEL_FEATURE_KEYS = [
    "temperature",
    "pressure",
    "vibration",
]


_model = None


def load_model():
    global _model

    if _model is not None:
        return _model

    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "Risk model is not available. "
                "Run the ML training script first."
            ),
        )

    try:
        _model = joblib.load(MODEL_PATH)
        return _model

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Risk model could not be loaded.",
        ) from exc


def get_prediction_features(
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

    machine_values = {
        value.field.key: value.value
        for value in machine.values
    }

    missing_features = [
        feature
        for feature in MODEL_FEATURE_KEYS
        if feature not in machine_values
        or machine_values[feature] is None
        or str(machine_values[feature]).strip() == ""
    ]

    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=(
                "Machine is missing required model "
                "features: "
                + ", ".join(missing_features)
            ),
        )

    try:
        temperature = float(
            machine_values["temperature"]
        )

        pressure = float(
            machine_values["pressure"]
        )

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Temperature and Pressure must "
                "contain valid numeric values."
            ),
        ) from exc

    vibration = str(
        machine_values["vibration"]
    )

    return {
        "temperature": temperature,
        "pressure": pressure,
        "vibration": vibration,
    }


def predict_machine_risk(
    machine_id: int,
    db: Session,
):
    features = get_prediction_features(
        machine_id,
        db,
    )

    model = load_model()

    input_data = pd.DataFrame(
        [
            {
                "temperature": features["temperature"],
                "pressure": features["pressure"],
                "vibration": features["vibration"],
            }
        ]
    )

    try:
        prediction = model.predict(
            input_data
        )[0]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Risk prediction failed.",
        ) from exc

    return {
        "machine_id": machine_id,
        "risk_level": str(prediction),
        "features_used": features,
    }