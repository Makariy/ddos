from typing import List, Union
from asyncio import sleep

from sanic.server.websockets.impl import WebsocketImplProtocol

from models import Client
from services.action_services import get_action
from lib.utils import get_app


async def wait_for_action(ws):
    """Enters infinite loop until action appears"""
    while True:
        if await get_action() is not None:
            return
        await sleep(0.1)


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


