from typing import Union
import json
from websockets import WebSocketClientProtocol

from models import Action


async def get_server_command(websocket):
    return json.loads(await websocket.recv())


async def get_action(websocket: WebSocketClientProtocol) -> Union[Action, None]:
    response = json.loads(await websocket.recv())
    return Action(**response.get('action'))

