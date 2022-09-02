from pydantic import BaseModel

# request models

class IncomingSMS(BaseModel):
    recipient_id: str
    sender_id: str
    sms_text: str
