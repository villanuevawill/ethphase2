import asyncio
import functools
import json
import logging
import socket
import websockets
from config import system_config
from pydispatch import dispatcher


class Server:
    def __init__(self):
        self.port = system_config["PORT"]
        # self.shard_count = system_config["SHARD_COUNT"]

    def run(self):
        # We need an event loop just to handle incoming events
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(hello, socket.gethostbyname(''), self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

# This coroutine is run once for each socket connection.
async def hello(websocket, path):
    logging.info(f"Websocket object connected on path {path} from {websocket.host}")

    # These must stay in scope
    handlers = []

    # Receive new shard blocks
    loop = asyncio.new_event_loop()
    # loop.run_forever()
    # loop = asyncio.get_event_loop()
    for i in range(system_config["SHARD_COUNT"]):
        logging.info(f"Server    : Listening for events from shard {i}")

        # Spawn a handler to manage this shard
        handler = Handler(websocket, loop, signal=f"SHARD_{i}")
        handlers.append(handler)

    # Handshake
    await websocket.send('Hello, world!')

    while True:
        await websocket.ping()
        await asyncio.sleep(2)


class Handler:
    def __init__(self, websocket, loop, signal):
        logging.info(f"Handler created for signal {signal} on websocket {websocket}")
        self.websocket = websocket
        self.signal = signal
        dispatcher.connect(self.receive, signal=signal)
        self.loop = loop
        # self.loop = asyncio.new_event_loop()
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.set_event_loop(loop)
        # asyncio.get_event_loop().run_forever()
        # self.loop.run_forever()
        # loop.run_forever()

    def receive(self, message, shard):
        logging.info(f"GOT BLOCK: {message.root} slot {message.slot} on shard {shard}")
        # task = asyncio.create_task(self.__async_send(block=message, shard=shard))
        return asyncio.create_task(self.__async_send(block=message, shard=shard))
        # return self.loop.run_until_complete(self.__async_send(block=message, shard=shard))
        # return self.loop.call_soon_threadsafe(self.__async_send(block=message, shard=shard))
        # return asyncio.get_running_loop().call_soon(self.__async_send(block=message, shard=shard))

    async def __async_send(self, block, shard):
        await self.websocket.send(f"got new block {block.root} slot {block.slot} on shard {shard}")

