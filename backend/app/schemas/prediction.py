from pydantic import BaseModel


class PredictionRequest(BaseModel):
    machine_id: int


class PredictionFeatures(BaseModel):
    temperature: float
    pressure: float
    vibration: str


class PredictionResponse(BaseModel):
    machine_id: int
    risk_level: str
    features_used: PredictionFeatures