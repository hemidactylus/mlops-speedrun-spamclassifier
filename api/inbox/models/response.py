from pydantic import BaseModel

# response models

class SuccessStatus(BaseModel):
    success: bool
    reason: str
