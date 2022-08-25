from fastapi import APIRouter

model_wrapper_cache = {}

def createModelRouter(version, model_wrapper):

    model_wrapper_cache[version] = model_wrapper

    modelRouter = APIRouter(
        prefix='/model/%s' % version,
    )

    @modelRouter.get('/process')
    async def process(txt):
        return {'result': model_wrapper_cache[version].text_to_prediction(txt)}

    return modelRouter
