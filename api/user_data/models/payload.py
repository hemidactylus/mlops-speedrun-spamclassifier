from pydantic import BaseModel

# request models

class NewSMS(BaseModel):
    sender_id: str
    sms_text: str
