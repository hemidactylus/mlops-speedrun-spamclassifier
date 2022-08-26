from pydantic import BaseModel
from typing import List

# request models

class TextInput(BaseModel):
    text: str
    echo_input: bool = False
    skip_cache: bool = False

class FeatureInput(BaseModel):
    features: List[float]
    echo_input: bool = False
    skip_cache: bool = False
