from importlib import util
from chimumin import Chimumin
import asyncio
from aioconsole import (ainput, aprint)
import os
import sys

chimumin = Chimumin("https://matrix.org", os.environ["MATRIX_USERNAME"])

async def synchronize():
    response = await chimumin.login(os.environ["MATRIX_PASSWORD"])
    print(response)
    await chimumin.sync_forever(1000)
    print('[SYSTEM]: Ready.')


async def get_input():
    while True:
        await aprint(await ainput())


async def main():
    task1 = asyncio.create_task(synchronize())
    task2 = asyncio.create_task(get_input())
    await asyncio.wait([task1, task2])


if __name__ == "__main__":
    print('Running main.')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        pass
    finally:
        loop.close()


async def process_command(text):
    print(f'Processing command: {text}')

    if len(text) > 0 and text[0] == "/":
        text = text[1:]
        command = text.split(' ')[0]
        await chimumin.run_command(command, text[len(command) + 1:])


# await chimumin._synced(await chimumin.sync())