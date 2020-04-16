from importlib import util
from chimumin import Chimumin
import asyncio
import os
import curses
from curses.textpad import (rectangle, Textbox)
from curses import (newwin, wrapper)

chimumin = None


async def process_command(text):
    # chimumin.printchat('Processing command: {}\n'.format(text))

    if len(text) > 0 and text[0] == "/":
        text = text[1:]
        command = text.split(' ')[0]
        await chimumin.run_command(command, text[len(command) + 1:])


async def synchronize():
    response = await chimumin.login(os.environ["MATRIX_PASSWORD"])

    response = await chimumin.sync()

    await chimumin.r_callbacks['_sync_response']['func'](chimumin, response)

    await chimumin.run_command('ls')

    await chimumin.sync_forever(1000)


# https://stackoverflow.com/questions/48803765/is-there-a-way-to-getkey-getchar-asynchronously-in-python
from threading import Thread

event_loop = None

def _get_input(stdscr):
    (Y, X) = stdscr.getmaxyx()

    cmdwin = newwin(1, X - 2, Y - 3, 1)

    cmdbox = Textbox(cmdwin)
    cmdbox.stripspaces = True
    cmdbox.edit()
    message = cmdbox.gather().strip()
    cmdwin.refresh()
    
    asyncio.run_coroutine_threadsafe(process_command(message), event_loop)


def get_input():
    while True:
        wrapper(_get_input)
#


async def start(stdscr):
    task1 = asyncio.create_task(synchronize())
    # task2 = asyncio.create_task(get_input(stdscr))
    await asyncio.wait([task1])
    # await asyncio.wait([task1, task2])


def init_window(stdscr):
    curses.echo(False)

    stdscr.clear()
    # stdscr.keypad(True)

    (Y, X) = stdscr.getmaxyx()
    
    rectangle(stdscr, 1, 0, Y - 5, (X - 4 + 1) // 2 + 1)
    rectangle(stdscr, 1, (X - 4) // 2 + 3, Y - 5, X - 1)
    rectangle(stdscr, Y - 4, 0, Y - 2, X - 1)
    stdscr.refresh()
    
    stdscr.addstr(0, 0, "chimumin - yet another matrix client ")
    stdscr.refresh()

    chatwin = newwin(Y - 7, (X - 4 + 1) // 2, 2, 1)
    chatwin.scrollok(True)

    syswin = newwin(Y - 7, (X - 4) // 2, 2, (X - 4) // 2 + 4)
    syswin.scrollok(True)
    
    global chimumin
    chimumin = Chimumin("https://matrix.org", os.environ["MATRIX_USERNAME"], chatwin, syswin)


def end_window(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

    stdscr.refresh()


def main(stdscr):    
    init_window(stdscr)

    global scr
    scr = stdscr

    global event_loop
    
    event_loop = asyncio.get_event_loop()
    loop = event_loop

    thread = Thread(target = get_input)
    thread.start()
    
    try:
        loop.run_until_complete(start(stdscr))
    except Exception as e:
        pass
    finally:
        loop.close()
    
    end_window(stdscr)

    # while True:
    #     pass


if __name__ == "__main__":
    curses.wrapper(main)
