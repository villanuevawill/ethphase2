import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii
from config import system_config

EPOCH_TIME = 15

class Beacon():
    def __init__(self):
        self.slots = []
        self.shard_count = system_config["SHARD_COUNT"]

    def run(self):
        for i in range(0, self.shard_count):
            dispatcher.connect(self.handle_shard_write, signal=f"SHARD_TO_BEACON_{i}")

    def handle_shard_write(self, blocks, shard):
        logging.info("writing!")



# def beacon(shard_count):
#     slots = []

#     dispatcher.connect()
        # for i in range(0, shard_count):
        #     logging.info(f"publishing beacon request for shard {i}")
        #     dispatcher.send(signal=f"BEACON_SHARD_{i}")
