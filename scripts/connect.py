import logging
import sys
import asyncio

from websockets.exceptions import ConnectionClosed

from scripts.services.communication_services import wait_for_command_from_server, \
    get_action, \
    is_needed_to_stop
from scripts.services.connect_services import connect, register
from scripts.services.attack_services import start_attack


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__package__)


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

    action = await get_action(websocket)
    logger.info(f"Starting attack on: {action.target}")

    try:
        attack = await start_attack(action.target)
        while True:
            if attack.done():
                logger.info(f"attack stopped on {action.target}")
                break
            command = await wait_for_command_from_server(websocket)
            if command is not None and await is_needed_to_stop(command):
                logger.info(f"server communicated to stop attack on {action.target}")
                attack.cancel()
                break

    except ConnectionClosed as e:
        logger.error(f"Connection was closed: {e}")
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
