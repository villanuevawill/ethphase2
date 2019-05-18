import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii

EPOCH_TIME = 15

class Beacon():
    def __init__(self, shard_count):
        self.slots = []
        self.shard_count = shard_count

    def run(self):
        for i in range(0, self.shard_count):
            dispatcher.connect(self.handle_shard_write, signal=f"SHARD_TO_BEACON_{i}")
        time.sleep(1000000)

    def handle_shard_write(self, blocks, shard):
        logging.info("writing!")



# def beacon(shard_count):
#     slots = []

#     dispatcher.connect()
        # for i in range(0, shard_count):
        #     logging.info(f"publishing beacon request for shard {i}")
        #     dispatcher.send(signal=f"BEACON_SHARD_{i}")
