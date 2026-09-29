from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from app.services.prediction_service import (
    predict_machine_risk,
)


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


@router.post(
    "",
    response_model=PredictionResponse,
)
def predict_risk(
    payload: PredictionRequest,
    db: Session = Depends(get_db),
):
    return predict_machine_risk(
        payload.machine_id,
        db,
    )