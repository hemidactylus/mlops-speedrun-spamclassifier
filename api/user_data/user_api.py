import uuid
from typing import List
from fastapi import FastAPI, Depends, Response, status

from api.tools.localCORS import permitReactLocalhostClient

from api.user_data.config.config import getSettings

from api.user_data.storage.db_io import (
    retrieve_sms,
    retrieve_smss_by_sms_id,
    store_sms,
)
from api.user_data.utils.db_dependency import g_get_session
from api.user_data.models.response import DateRichSMS, InsertionSuccess
from api.user_data.models.payload import NewSMS


settings = getSettings()
architecture_version = settings.arch_version

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

if architecture_version == 'II':
    @app.post('/sms/{user_id}', response_model=InsertionSuccess)
    async def post_sms(user_id, newSMS: NewSMS, session=Depends(g_get_session)):
        sms_id = uuid.uuid1()
        try:
            store_sms(session, user_id, sms_id, newSMS.sender_id, newSMS.sms_text)
            return InsertionSuccess(
                successful=True,
                msg=f'SMS from {newSMS.sender_id} to {user_id} inserted.',
                sms_id=str(sms_id),
            )
        except Exception as e:
            return InsertionSuccess(successful=False, msg=str(e))
