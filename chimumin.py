from importlib import util
from nio import (AsyncClient, SyncResponse, RoomNameEvent, RoomAliasEvent)
import asyncio
import datetime

class Chimumin(AsyncClient):
    commands = {}
    

    def printchat(self, text, system = False, time = True):
        text = ": " + text
        if system:
            text = '[SYSTEM]' + text
        
        if time:
            a = datetime.datetime.now()
            text = '[' + ("%s:%s:%s.%s" % (a.hour, a.minute, a.second, str(a.microsecond)[:2])) + ']' + text

        self.chatwin.addstr(text)
        self.chatwin.refresh()


    async def sync_rooms(self, rooms):
        for id in rooms.join:
            for event in rooms.join[id].timeline.events:
                # self.printchat('{} : {}\n'.format(id, type(event)), True)
                if isinstance(event, RoomNameEvent):
                    name = event.name

                    if id not in self.room_names:
                        self.room_ids[name] = id
                        self.room_names[id] = name
                    else:
                        del self.room_ids[room.names[id]]
                        self.room_names[id] = name
                        self.room_ids[name] = id
                
                elif isinstance(event, RoomAliasEvent):
                    name = event.canonical_alias

                    if id not in self.room_names:
                        self.room_ids[name] = id
                        self.room_names[id] = name
                    else:
                        del self.room_ids[room.names[id]]
                        self.room_names[id] = name
                        self.room_ids[name] = id


    async def _synced(self, response):
        # self.printchat("We synced, token: {}\n".format(response.next_batch), True)
        self.next_batch = response.next_batch
        await self.sync_rooms(response.rooms)
    

    def __init__(self, homeserver, username, chatwin):
        super().__init__(homeserver, username)
        self.add_response_callback(self._synced, SyncResponse)
        self.chatwin = chatwin
        self.room_names = {}
        self.room_ids = {}
        self.current_room_id = ""
    

    async def run_command(self, command, content = None):
        if command in self.commands:
            # self.printchat('Processing {} with {}.\n'.format(command, content), True)
            await self.commands[command](self, content)


def command(f):
    print(f'Adding {f.__name__} to the commands')
    Chimumin.commands[f.__name__] = f
    print('Added.')


@command
async def send(self, text):
    if self.current_room_id not in self.room_names.keys():
        self.printchat('Not in a room.\n', True)
        return
    
    self.printchat('Sending {} message to {}\n'.format(text, self.room_names[self.current_room_id]), True)
    await self.room_send(self.current_room_id, 'm.room.message', content={
            "msgtype": "m.text",
            "body": text
        })
    self.printchat('Sent.\n', True)


@command
async def room(self, text):
    self.printchat('Changing room to {}\n'.format(text), True)

    if text not in self.room_ids.keys():
        self.printchat('Invalid room name.\n', True)
        return

    self.current_room_id = self.room_ids[text]
    self.printchat('Room changed.\n', True)


@command
async def ls(self, text = None):
    self.printchat("Listing joined rooms:\n", True)

    for name in self.room_ids:
        self.printchat('{} -> {}\n'.format(name, self.room_ids[name]), True)
