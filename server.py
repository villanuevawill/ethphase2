import asyncio
import socket
import websockets
from config import system_config


class Server:
    def __init__(self):
        self.port = system_config["PORT"]

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.hello, socket.gethostbyname(''), self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    @staticmethod
    async def hello(websocket, path):
        await websocket.send('Hello, world!')
        # name = await websocket.recv()
        # print(f"< {name}")
        #
        # greeting = f"Hello {name}!"
        #
        # await websocket.send(greeting)
        # print(f"> {greeting}")

