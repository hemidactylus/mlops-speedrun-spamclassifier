from pydantic import BaseModel
from typing import List, Optional, Dict

class FeaturesResult(BaseModel):
    features: List[float]


class PredictionTopInfo(BaseModel):
    label: str
    value: float


class PredictionResult(BaseModel):
    input: Optional[str]
    prediction: Dict[str, float]
    top: Optional[PredictionTopInfo]
    from_cache: bool = False
