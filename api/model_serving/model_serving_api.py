import os
from fastapi import FastAPI

from api.model_serving.routers.model_router import createModelRouter
    
from api.model_serving.aimodels.RandomForestModel import RandomForestModel
from analysis.features1.feature1_extractor import Feature1Extractor

base_dir = os.path.abspath(os.path.dirname(__file__))
models_dir = os.path.join(base_dir, '..', '..', 'models')

EXPOSED_VERSIONS = ['v1']

apiDescription="""
Spam Classifier API

An API exposing spam-classifier models
"""

tags_metadata = [
    {
        'name': version,
        'description': 'Model version %s' % version,
    }
    for version in EXPOSED_VERSIONS
]

app = FastAPI(
    title="Spam Model API",
    description=apiDescription,
    version="1.0",
    openapi_tags=tags_metadata,
)

# include router(s)
if 'v1' in EXPOSED_VERSIONS: # expose model v1 2019
    model_v1 = RandomForestModel(
        model_path=os.path.join(models_dir, 'model1_2019', 'model1.pkl'),
        feature_extractor=Feature1Extractor(),
        output_labels=['ham', 'spam'],
    )
    app.include_router(createModelRouter('v1', model_v1))
