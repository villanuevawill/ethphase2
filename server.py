import asyncio
import datetime
import functools
import logging
import random
import socket
import websockets
from config import system_config
from pydispatch import dispatcher


class Server:
    def __init__(self):
        self.port = system_config["PORT"]
        self.shard_count = system_config["SHARD_COUNT"]

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.hello, socket.gethostbyname(''), self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    # @staticmethod
    # This coroutine is run once for each socket connection.
    async def hello(self, websocket, path):
        logging.info(f"Websocket object connected on path {path} from {websocket.host}")

        # These must stay in scope
        handlers = []

        # Receive new shard blocks
        for i in range(self.shard_count):
            logging.info(f"Server    : Listening for events from shard {i}")

            # Spawn a handler to manage this shard
            handler = Handler(websocket, signal=f"SHARD_{i}")
            handlers.append(handler)
            # await handler.send()
            # handlers.append(Handler(websocket, signal=f"SHARD_{i}"))

        # Handshake
        await websocket.send('Hello, world!')

        while True:
            await websocket.ping()
            await asyncio.sleep(2)
            # now = datetime.datetime.utcnow().isoformat() + 'Z'
            # await websocket.send(now)
            # await asyncio.sleep(random.random() * 3)
        # name = await websocket.recv()
        # print(f"< {name}")
        #
        # greeting = f"Hello {name}!"
        #
        # await websocket.send(greeting)
        # print(f"> {greeting}")


class Handler:
    def __init__(self, websocket, signal):
        logging.info(f"Handler created for signal {signal} on websocket {websocket}")
        self.websocket = websocket
        self.signal = signal
        dispatcher.connect(self.receive, signal=signal)
        self.loop = asyncio.new_event_loop()

    # async def send(self):
    #     await self.websocket.send("handshake")

    def receive(self):
        logging.info("GOT BLOCK")
        # loop = asyncio.get_event_loop()
        # future = asyncio.Future()
        # asyncio.run(asyncio.coroutine(self.send))
        # asyncio.set_event_loop(asyncio.new_event_loop())
        # asyncio.ensure_future(self.websocket.send("handshake"))

        # self.websocket.send(f"Got block from shard {self.signal}")

        return self.loop.run_until_complete(self.__async_send())

    async def __async_send(self):
        await self.websocket.send("handshake")

