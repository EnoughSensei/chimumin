import curses
from curses.textpad import (rectangle, Textbox)
from curses import (newwin, wrapper, newpad)
from time import time

def main():
    (Y, X) = stdscr.getmaxyx()
    
    rectangle(stdscr, Y - 2, 0, Y - 2, X - 1)
    stdscr.refresh()
    
    stdscr.addstr(0, 0, "chimumin - yet another matrix client")
    stdscr.refresh()

    chatwin = newwin(30, X, 0, 0)
    chatwin.scrollok(True)
    curses.echo(False)

    chatbox = Textbox(chatwin)
    chatpad = newpad(Y - 2, X)
    
    chatwin.addstr('temp\n')
    chatwin.refresh()

    chatpad_pos = 0
    chatpad.refresh(chatpad_pos, 0, 1, 0, Y - 2, X)

    for i in range(20):
        chatwin.addstr('temp {}\n'.format(i))
        # chatwin.refresh()
        chatpad.refresh(chatpad_pos, 0, 1, 0, Y - 2, X)
