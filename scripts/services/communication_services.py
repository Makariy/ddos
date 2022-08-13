from typing import Union
import json
from sanic.server.websockets.impl import WebsocketImplProtocol
from lib.utils import wait_for
from models import Action, BaseCommand


async def get_command_from_server(ws: WebsocketImplProtocol):
    return BaseCommand(**json.loads(await ws.recv()))


async def wait_for_command_from_server(ws: WebsocketImplProtocol):
    return await wait_for(get_command_from_server(ws), 0.1)


async def get_action(ws: WebsocketImplProtocol) -> Union[Action, None]:
    response = json.loads(await ws.recv())
    return Action(**response.get('action'))


async def is_needed_to_stop(command: BaseCommand) -> bool:
    if command.title == 'stop':
        return True
    return False




