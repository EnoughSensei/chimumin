from importlib import util
from nio import (AsyncClient, SyncResponse, RoomMessageText, RoomNameEvent, RoomAliasEvent)
import asyncio
import datetime
import types

class Chimumin(AsyncClient):
    commands = {}
    r_callbacks = {}
    e_callbacks = {}


    def printchat(self, text, time = True):
        if time:
            a = datetime.datetime.now()
            text = '[' + ("%s:%s:%s.%s" % (a.hour, a.minute, a.second, str(a.microsecond)[:2])) + ']' + text

        self.chatwin.addstr(text)
        self.chatwin.refresh()
    

    def printsystem(self, text, time = True):
        if time:
            a = datetime.datetime.now()
            text = '[' + ("%s:%s:%s.%s" % (a.hour, a.minute, a.second, str(a.microsecond)[:2])) + ']' + text

        self.syswin.addstr(text)
        self.syswin.refresh()
    

    def __init__(self, homeserver, username, chatwin, syswin):
        super().__init__(homeserver, username)
        
        self.chatwin = chatwin
        self.syswin = syswin

        for cb in self.r_callbacks:
            f = self.r_callbacks[cb]['func']
            e = self.r_callbacks[cb]['type']
            self.add_response_callback(types.MethodType(f, self), e)
        
        for cb in self.e_callbacks:
            f = self.e_callbacks[cb]['func']
            e = self.e_callbacks[cb]['type']
            self.add_event_callback(types.MethodType(f, self), e)
        
        self.current_room_id = ""
    

    async def run_command(self, command, content = None):
        if command in self.commands:
            await self.commands[command](self, content)


def response_callback(type):
    def _callback(f):
        Chimumin.r_callbacks[f.__name__] = {}
        Chimumin.r_callbacks[f.__name__]['func'] = f
        Chimumin.r_callbacks[f.__name__]['type'] = type
    return _callback


def event_callback(type):
    def _callback(f):
        Chimumin.e_callbacks[f.__name__] = {}
        Chimumin.e_callbacks[f.__name__]['func'] = f
        Chimumin.e_callbacks[f.__name__]['type'] = type
    return _callback


@event_callback(RoomNameEvent)
async def _room_name_event(self, source, event):
    self.printsystem(format_event_message('A room is renamed to {} by {}.'.format(event.name, event.sender), 'm.room.name'))


@event_callback(RoomAliasEvent)
async def _room_alias_event(self, source, event):
    self.printsystem(format_event_message('The alias of a room is changed to {}.'.format(event.canoncial_alias), 'm.room.aliases'))


@event_callback(RoomMessageText)
async def _room_message_text(self, source, event):
    text = event.body
    name = event.sender
    room_name = source.display_name
    self.printchat(format_message(text, name, room_name))


@response_callback(SyncResponse)
async def _sync_response(self, response):
    self.next_batch = response.next_batch


def command(f):
    print(f'Adding {f.__name__} to the commands')
    Chimumin.commands[f.__name__] = f
    print('Added.')


@command
async def send(self, text):
    if self.current_room_id not in self.rooms:
        self.printsystem(format_system_message('Not in a room.'))
        return
    
    self.printsystem(format_system_message('Sending {} message to {}'.format(text, self.rooms[self.current_room_id].display_name)))
    await self.room_send(self.current_room_id, 'm.room.message', content={
            "msgtype": "m.text",
            "body": text
        })
    self.printsystem(format_system_message('Sent.'))


@command
async def room(self, text):
    self.printsystem(format_system_message('Changing room to {}.'.format(text)))

    for id in self.rooms:
        if self.rooms[id].display_name == text:
            self.current_room_id = id
            self.printsystem(format_system_message('Room changed.'))
            return
    
    self.printsystem(format_system_message('Invalid room name.'))


@command
async def ls(self, text = None):
    self.printsystem(format_system_message("Listing joined rooms:"))

    for id in self.rooms:
        self.printsystem(format_system_message(self.rooms[id].display_name))
    
    self.printsystem(format_system_message("End of list."))


def format_message(text, sender = "", room = ""):
    return '[{}][{}]: {}\n'.format(room, sender, text)


def format_system_message(text):
    return '[SYSTEM]: {}\n'.format(text)


def format_event_message(text, event_type = ""):
    return '[{}]: {}\n'.format(event_type, text)
