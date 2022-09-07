from operator import itemgetter
from fastapi import APIRouter, Depends, Request
from typing import List

from api.model_serving.utils.db_dependency import g_get_session
from api.model_serving.storage.db_io import store_cached_prediction, retrieve_cached_prediction, store_call_log_item, retrieve_call_log

from api.model_serving.models.payload import TextInput, FeatureInput
from api.model_serving.models.response import FeaturesResult, PredictionResultFromText, PredictionResultFromFeatures
from api.model_serving.models.call_log import CallLogEntry

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


def _format_prediction(pred_dict, input, echo_input, from_cache, model_class):
    result = {
        **{
            'prediction': pred_dict,
            'top': _get_top_prediction(pred_dict),
            'from_cache': from_cache,
        },
        **({'input': input} if echo_input else {}),
    }
    return model_class(**result)


def _format_features(features, input, echo_input, from_cache):
    return FeaturesResult(**{
        **{
            'features': features,
            'from_cache': from_cache,
        },
        **({'input': input} if echo_input else {}),
    })


def createModelRouter(version, model_wrapper):

    model_wrapper_cache[version] = model_wrapper

    modelRouter = APIRouter(
        prefix='/model/%s' % version,
    )

    @modelRouter.post('/text_to_features', response_model=FeaturesResult, tags=[version])
    async def serve_text_to_features(params: TextInput, request: Request, session=Depends(g_get_session)):
        # try cache:
        cached = None if params.skip_cache else retrieve_cached_prediction(session, 'text_to_features', version=version, input=params.text)
        # act accordingly
        if cached:
            features = cached
            from_cache = True
        else:
            features = model_wrapper_cache[version].text_to_features(params.text)
            from_cache = False
            store_cached_prediction(session, 'text_to_features', version=version, input=params.text, output=features)
        #
        caller_id = request.client[0]
        store_call_log_item(session, caller_id, 'text_to_features', version=version, input=params.text)
        return _format_features(
            features=features,
            input=params.text,
            echo_input=params.echo_input,
            from_cache=from_cache,
        )

    @modelRouter.post('/features_to_prediction', response_model=PredictionResultFromFeatures, tags=[version])
    async def serve_features_to_prediction(params: FeatureInput, request: Request, session=Depends(g_get_session)):
        # try cache:
        cached = None if params.skip_cache else retrieve_cached_prediction(session, 'features_to_prediction', version=version, input=params.features)
        # act accordingly
        if cached:
            prediction_dict = cached
            from_cache = True
        else:
            prediction_dict = model_wrapper_cache[version].features_to_prediction(params.features)
            from_cache = False
            store_cached_prediction(session, 'features_to_prediction', version=version, input=params.features, output=prediction_dict)
        #
        caller_id = request.client[0]
        store_call_log_item(session, caller_id, 'features_to_prediction', version=version, input=params.features)
        return _format_prediction(
            prediction_dict,
            params.features,
            params.echo_input,
            from_cache=from_cache,
            model_class=PredictionResultFromFeatures,
        )

    @modelRouter.post('/text_to_prediction', response_model=PredictionResultFromText, tags=[version])
    async def serve_text_to_prediction(params: TextInput, request: Request, session=Depends(g_get_session)):
        # try cache:
        cached = None if params.skip_cache else retrieve_cached_prediction(session, 'text_to_prediction', version=version, input=params.text)
        # act accordingly
        if cached:
            prediction_dict = cached
            from_cache = True
        else:
            prediction_dict = model_wrapper_cache[version].text_to_prediction(params.text)
            from_cache = False
            store_cached_prediction(session, 'text_to_prediction', version=version, input=params.text, output=prediction_dict)
        caller_id = request.client[0]
        store_call_log_item(session, caller_id, 'text_to_features', version=version, input=params.text)
        return _format_prediction(
            prediction_dict,
            params.text,
            params.echo_input,
            from_cache=from_cache,
            model_class=PredictionResultFromText,
        )

    @modelRouter.get('/recent_call_log', response_model=List[CallLogEntry], tags=[version])
    async def get_call_log(request: Request, session=Depends(g_get_session)):
        caller_id = request.client[0]
        return retrieve_call_log(session, caller_id, version)

    return modelRouter
