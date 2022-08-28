import uuid
from typing import List
from fastapi import FastAPI, Depends, Response, status

from api.tools.localCORS import permitReactLocalhostClient

from api.user_data.storage.db_io import (
    retrieve_sms,
    retrieve_smss_by_sms_id,
)
from api.user_data.utils.db_dependency import g_get_session
from api.user_data.utils.models import DateRichSMS

apiDescription="""
SMS Data API

An API for users to access their SMS inbox
"""

app = FastAPI(
    title="SMS Data Api",
    version="1.0",
    description=apiDescription,
)

# this is really a 'demo mode' thing which should be refined!
permitReactLocalhostClient(app)

@app.get('/sms/{user_id}/{sms_id_str}', response_model=DateRichSMS)
async def get_sms(user_id, sms_id_str, response: Response, session=Depends(g_get_session)):
    sms_id = uuid.UUID(sms_id_str)
    sms = retrieve_sms(session, user_id, sms_id)
    if sms:
        return sms
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return sms


@app.get('/sms/{user_id}', response_model=List[DateRichSMS])
async def get_smss(user_id, session=Depends(g_get_session)):
    smss = retrieve_smss_by_sms_id(session, user_id)
    return smss
