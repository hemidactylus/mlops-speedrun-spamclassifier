from pydantic import BaseModel
from typing import List, Optional, Dict

class FeaturesResult(BaseModel):
    input: Optional[str]
    features: List[float]
    from_cache: bool = False


class PredictionTopInfo(BaseModel):
    label: str
    value: float


class PredictionResultFromText(BaseModel):
    input: Optional[str]
    prediction: Dict[str, float]
    top: Optional[PredictionTopInfo]
    from_cache: bool = False


class PredictionResultFromFeatures(BaseModel):
    input: Optional[List[float]]
    prediction: Dict[str, float]
    top: Optional[PredictionTopInfo]
    from_cache: bool = False
