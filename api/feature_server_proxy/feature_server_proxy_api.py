import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from api.tools.localCORS import permitReactLocalhostClient

apiDescription="""
Feast server proxy

An API to allow browser-to-feature-server requests
"""

app = FastAPI(
    title="Feast server proxy",
    version="1.0",
    description=apiDescription,
)

# this is really a 'demo mode' thing which should be refined!
permitReactLocalhostClient(app)


class FeatureRequestEntities(BaseModel):
    sms_id: List[str]


class FeatureRequest(BaseModel):
    feature_service: str
    entities: FeatureRequestEntities


@app.post('/get-online-features')
async def get_online_features(params: FeatureRequest):
    fs_response = requests.post(
        'http://localhost:6566/get-online-features',
        json=params.dict(),
    ).json()
    return fs_response
