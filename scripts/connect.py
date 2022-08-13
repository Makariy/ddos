import sys
import asyncio

from websockets.exceptions import ConnectionClosed

from lib.utils import wait_for
from scripts.services.communication_services import get_server_command, get_action
from scripts.services.connect_services import connect, register
from scripts.services.attack_services import start_attack


async def start(addr: str):
    websocket = await connect(addr)
    if websocket is None:
        print("Connection refused during connecting to the server")
        return -1

    registration = await register(websocket)
    if registration is None:
        print("Error trying to register this device on server")
        return -2

    action = await get_action(websocket)
    print(f"Starting attack on: {action.target}")

    try:
        attack, is_attack_running = await start_attack(action.target)
        while True:
            if await is_attack_running():
                print(f"attack stopped on {action.target}")
                break
            message = await wait_for(get_server_command(websocket), 0.1)
            if message is not None and message['command'].get('title') == 'stop':
                print(f"server communicated to stop attack on {action.target}")
                attack.cancel()
                break

    except ConnectionClosed as e:
        print("Connection was closed: ", e)
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
