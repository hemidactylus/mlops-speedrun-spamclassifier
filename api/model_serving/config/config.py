from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    model_versions: str = Field('v1', env='SPAM_MODEL_VERSIONS')


@lru_cache()
def getSettings():
    return Settings()
