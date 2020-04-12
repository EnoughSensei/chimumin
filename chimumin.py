from importlib import util
from nio import (AsyncClient, SyncResponse, RoomNameEvent, RoomAliasEvent)
import asyncio


class Chimumin(AsyncClient):
    commands = {}
    room_names = {}
    room_ids = {}
    current_room_id = ""
    last_batch = ""

    async def sync_rooms(self, rooms):
        for id in rooms.join:
            for event in rooms.join[id].timeline.events:
                print(f'{id} : {type(event)}')
                if isinstance(event, RoomNameEvent):
                    name = event.name

                    if not id in self.room_names:
                        self.room_ids[name] = id
                        self.room_names[id] = name
                    else:
                        del self.room_ids[room.names[id]]
                        self.room_names[id] = name
                        self.room_ids[name] = id
                
                elif isinstance(event, RoomAliasEvent):
                    name = event.canonical_alias

                    if not id in self.room_names:
                        self.room_ids[name] = id
                        self.room_names[id] = name
                    else:
                        del self.room_ids[room.names[id]]
                        self.room_names[id] = name
                        self.room_ids[name] = id

    async def _synced(self, response):
        print(f"We synced, token: {response.next_batch}")
        self.last_batch = response.next_batch
        await self.sync_rooms(response.rooms)
    
    def __init__(self, homeserver, username):
        super().__init__(homeserver, username)
        self.add_response_callback(self._synced, SyncResponse)
    
    async def run_command(self, command, content = None):
        if command in self.commands:
            await self.commands[command](self, content)

def command(f):
    print(f'Adding {f.__name__} to the commands')
    Chimumin.commands[f.__name__] = f
    print('Added.')

@command
async def send(self, text):
    print(f'Sending {text} message to {self.rooms[self.current_room_id].name}')
    await self.room_send(self.current_room_id, 'm.room.message', content={
            "msgtype": "m.text",
            "body": text
        })
    print('Sent.')

@command
async def room(self, text):
    print(f'Changing room to {text}')
    
    if not text in self.room_ids:
        print(f'Invalid room name.')
        return
    
    self.room_name = text
    self.current_room_id = self.room_ids[text]
    print('Room changed.')

@command
async def ls(self, text = None):
    print("Listing joined rooms:")

    for id in self.room_names:
        print(f'{id} -> {self.room_names[id]}')
    
    print('----------')