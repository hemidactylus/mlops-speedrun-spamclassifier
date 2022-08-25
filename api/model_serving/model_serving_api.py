import os
from fastapi import FastAPI

from api.model_serving.routers.model_router import createModelRouter
    
from api.model_serving.aimodels.RandomForestModel import RandomForestModel
from analysis.features1.feature1_extractor import Feature1Extractor

base_dir = os.path.abspath(os.path.dirname(__file__))
models_dir = os.path.join(base_dir, '..', '..', 'models')


app = FastAPI(
    title="Spam Model API",
    version="1.0",
)

# include router(s)
if True: # expose model v1 2019
    model_v1 = RandomForestModel(
        model_path=os.path.join(models_dir, 'model1_2019', 'model1.pkl'),
        feature_extractor=Feature1Extractor(),
        output_labels=['ham', 'spam'],
    )
    app.include_router(createModelRouter('v1', model_v1))
