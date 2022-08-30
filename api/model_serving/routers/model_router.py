from operator import itemgetter
from fastapi import APIRouter

from api.model_serving.models.payload import TextInput, FeatureInput
from api.model_serving.models.response import FeaturesResult, PredictionResultFromText, PredictionResultFromFeatures

model_wrapper_cache = {}


def _get_top_prediction(pred_dict):
    if len(pred_dict) == 0:
        return None
    else:
        topK, topV = sorted(
            pred_dict.items(),
            key=itemgetter(1),
            reverse=True,
        )[0]
        return {
            'label': topK,
            'value': topV,
        }

def _format_prediction(pred_dict, input, echo_input, model_class):
        result = {
            **{
                'prediction': pred_dict,
                'top': _get_top_prediction(pred_dict),
            },
            **({'input': input} if echo_input else {}),
        }
        return model_class(**result)


def createModelRouter(version, model_wrapper):

    model_wrapper_cache[version] = model_wrapper

    modelRouter = APIRouter(
        prefix='/model/%s' % version,
    )

    @modelRouter.post('/text_to_features', response_model=FeaturesResult, tags=[version])
    async def serve_text_to_features(params: TextInput):
        return FeaturesResult(**{'features': model_wrapper_cache[version].text_to_features(params.text)})

    @modelRouter.post('/features_to_prediction', response_model=PredictionResultFromFeatures, tags=[version])
    async def serve_features_to_prediction(params: FeatureInput):
        prediction_dict = model_wrapper_cache[version].features_to_prediction(params.features)
        return _format_prediction(prediction_dict, params.features, params.echo_input, PredictionResultFromFeatures)

    @modelRouter.post('/text_to_prediction', response_model=PredictionResultFromText, tags=[version])
    async def serve_text_to_prediction(params: TextInput):
        prediction_dict = model_wrapper_cache[version].text_to_prediction(params.text)
        return _format_prediction(prediction_dict, params.text, params.echo_input, PredictionResultFromText)

    return modelRouter
