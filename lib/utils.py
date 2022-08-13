from typing import Union, Any
import asyncio
import sanic
import config

from asyncio.exceptions import TimeoutError


def get_app() -> sanic.Sanic:
    return sanic.Sanic.get_app(config.SANIC_APP_NAME)


async def wait_for(coroutine, timeout: float) -> Union[Any, None]:
    try:
        return await asyncio.wait_for(coroutine, timeout)
    except TimeoutError:
        return None

