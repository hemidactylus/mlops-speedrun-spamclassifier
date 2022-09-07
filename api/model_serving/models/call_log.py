from pydantic import BaseModel
from datetime import datetime

# models to handle the call log

class CallLogEntry(BaseModel):
    called_at: datetime
    endpoint: str
    version: str
    input_json: str
