from api.model_serving.storage.db_connect import get_session


async def g_get_session():
    """
    In itself, the `get_session` function returns the connection.
    To make this interoperable with the FastAPI `Depends`-based dependency
    paradigm, here `get_session` is simply wrapped as an async function
    `yeld`ing the session.
    """
    yield get_session()
