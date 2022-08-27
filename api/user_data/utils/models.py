"""
Pydantic models representing the content of the database tables.
"""

from time_uuid import TimeUUID
from datetime import datetime
from pydantic import BaseModel
# Cassandra's TIMEUUID maps to Python's uuid1, and this is the typecast function:
from uuid import UUID

class SMS(BaseModel):
    user_id: str
    sms_id: UUID
    sender_id: str
    sms_text: str

class DateRichSMS(SMS):
    """
    Enrich a SMS by extracting the datetime from the sms_id
    to expose it in a friendly way. This trickery strictly is unnecessary,
    just a bit of kindness to our front-end.
    """
    date_sent: datetime

    @staticmethod
    def from_SMS(sms):
        _date_sent = datetime.fromtimestamp(TimeUUID(bytes=sms.sms_id.bytes).get_timestamp())
        return DateRichSMS(
            date_sent=_date_sent,
            **sms.dict(),
        )
