from typing import Union
import json
import asyncio

import websockets
from websockets import WebSocketClientProtocol


async def connect(addr: str) -> Union[WebSocketClientProtocol, None]:
    try:
        return await websockets.connect(f'ws://{addr}')
    except ConnectionRefusedError:
        return None


async def register(websocket):
    try:
        await websocket.send("PING")
        response = json.loads(await asyncio.wait_for(websocket.recv(), 5))
    except TimeoutError:
        response = {}

    if response.get('status') != "success":
        return None
    return response
