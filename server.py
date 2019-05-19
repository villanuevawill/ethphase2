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
            # async def bound_handler(message):
            #     await handle_shard_write(message, shard=i)
            # bound_handler = functools.partial(handle_shard_write, shard=i)
            logging.info(f"Server    : Listening for events from shard {i}")
            # dispatcher.connect(lambda message: handle_shard_write(message, shard=i), signal=f"SHARD_{i}")
            # dispatcher.connect(lambda message: logging.info("GOT BLOCK"), signal=f"SHARD_{i}")
            # dispatcher.connect(lambda message: logging.info("GOT BLOCK"))
            # dispatcher.connect(lambda message: logging.info("GOT BLOCK"), signal=f"SHARD_TO_BEACON_{i}")
            # dispatcher.connect(self.foo, signal=f"SHARD_{i}")

            # Spawn a handler to manage this shard
            handlers.append(Handler(websocket, signal=f"SHARD_{i}"))

        # Handshake
        await websocket.send('Hello, world!')

        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            await websocket.send(now)
            await asyncio.sleep(random.random() * 3)
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
        # dispatcher.connect(self.receive, signal=signal)
        dispatcher.connect(self.receive, signal=signal)

    def receive(self):
        logging.info("GOT BLOCK 2")

