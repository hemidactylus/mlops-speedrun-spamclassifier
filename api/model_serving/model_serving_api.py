import os
from fastapi import FastAPI

from api.tools.localCORS import permitReactLocalhostClient

from api.model_serving.routers.model_router import createModelRouter
    
from api.model_serving.aimodels.RandomForestModel import RandomForestModel
from analysis.features1.feature1_extractor import Feature1Extractor
from api.model_serving.config.config import getSettings


base_dir = os.path.abspath(os.path.dirname(__file__))
models_dir = os.path.join(base_dir, '..', '..', 'models')

settings = getSettings()
exposed_model_version_set = set(settings.model_versions.split(','))

print(f"[model_serving_api] Model versions being exposed: {' '.join(sorted(exposed_model_version_set))}")

apiDescription="""
Spam Classifier API

An API exposing spam-classifier models
"""

tags_metadata = [
    {
        'name': version,
        'description': 'Model version %s' % version,
    }
    for version in exposed_model_version_set
]

app = FastAPI(
    title="Spam Model API",
    description=apiDescription,
    version="1.0",
    openapi_tags=tags_metadata,
)

# this is really a 'demo mode' thing which should be refined!
permitReactLocalhostClient(app)

# include router(s)
if 'v1' in exposed_model_version_set: # expose model v1 2019
    model_v1 = RandomForestModel(
        model_path=os.path.join(models_dir, 'model1_2019', 'model1.pkl'),
        feature_extractor=Feature1Extractor(),
        output_labels=['ham', 'spam'],
    )
    app.include_router(createModelRouter('v1', model_v1))
