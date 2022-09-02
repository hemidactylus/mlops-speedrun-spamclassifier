import requests
import uuid
from datetime import datetime
from time_uuid import TimeUUID
from fastapi import FastAPI, Response, status

from api.inbox.config import (
    USER_DATA_API_URL,
    MODEL_SERVING_API_URL,
    FEATURE_MODEL_VERSION,
    FEATURE_SERVER_URL,
    TIMESTAMP_FORMAT,
    PUSH_SOURCE_NAME,
)

from api.tools.localCORS import permitReactLocalhostClient

from api.inbox.utils.preprocessing import _adjust_feature_map_for_store
from api.inbox.models.response import SuccessStatus
from api.inbox.models.payload import IncomingSMS

apiDescription="""
Inbox API

An API for external actors to notify of incoming messages
"""

app = FastAPI(
    title="Inbox Api",
    version="1.0",
    description=apiDescription,
)

# this is really a 'demo mode' thing which should be refined!
permitReactLocalhostClient(app)

@app.post('/sms', response_model=SuccessStatus)
async def post_sms(incomingSMS: IncomingSMS):
    """
    1. store the message in the DB
    2. get the "v2" features from the model-serving API
    3. store the message and the features to the feature server
    """
    _stage = 'user-data API'
    recipient_id = incomingSMS.recipient_id
    sender_id = incomingSMS.sender_id
    sms_text = incomingSMS.sms_text
    #
    sms_insertion = requests.post(
        f'{USER_DATA_API_URL}/sms/{recipient_id}',
        json={'sender_id': sender_id, 'sms_text': sms_text},
    )
    sms_insertion_json = sms_insertion.json()
    try:
        if sms_insertion_json['successful']:
            sms_id_str = sms_insertion_json['sms_id']
            #
            _stage = 'features from model API'
            sms_features_req = requests.post(
                f'{MODEL_SERVING_API_URL}/model/{FEATURE_MODEL_VERSION}/text_to_features',
                json={'text': sms_text},
            )
            sms_features_req_json = sms_features_req.json()
            sms_features_map0 = sms_features_req_json
            sms_features_map = _adjust_feature_map_for_store(sms_features_map0, FEATURE_MODEL_VERSION)
            #
            sms_timestamp = datetime.fromtimestamp(TimeUUID(bytes=uuid.UUID(sms_id_str).bytes).get_timestamp())
            #
            if sms_features_map:
                _stage = 'insertion to feature server'
                store_insertion = requests.post(
                    f'{FEATURE_SERVER_URL}/push',
                    json={
                        'push_source_name': PUSH_SOURCE_NAME,
                        'df': {
                            **{
                                'sms_id': [sms_id_str],
                                'event_timestamp': [sms_timestamp.strftime(TIMESTAMP_FORMAT)],                            
                            },
                            **sms_features_map,
                        },
                        'to': 'online_and_offline',
                    },
                )
                return SuccessStatus(
                    success=True,
                    reason='SMS received correctly',
                )
            else:
                return SuccessStatus(
                    success=False,
                    reason='Feature computation failed',
                )
        else:
            return SuccessStatus(
                success=False,
                reason='DB insertion failed',
            )
    except Exception as e:
        return SuccessStatus(
            success=False,
            reason=f'Error "{str(e)}" at stage "{_stage}"',
        )
