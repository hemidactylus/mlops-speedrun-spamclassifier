from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    arch_version: str = Field('I', env='ARCHITECTURE_VERSION')


@lru_cache()
def getSettings():
    return Settings()
