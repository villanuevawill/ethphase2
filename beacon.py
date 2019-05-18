import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii
from config import system_config


class Beacon():
    def __init__(self):
        self.slots = []
        self.shard_count = system_config["SHARD_COUNT"]

    def run(self):
        for i in range(0, self.shard_count):
            dispatcher.connect(self.handle_shard_write, signal=f"SHARD_TO_BEACON_{i}")

        while True:
            time.sleep(system_config["EPOCH_SLOT_TIME"])
            current_slot = len(self.slots) % system_config["SHARD_COUNT"]
            dispatcher.send(signal=f"BEACON_TO_SHARD_{current_slot}")

    def handle_shard_write(self, blocks, shard):
        self.slots.append(blocks)
        shard_count = system_config["SHARD_COUNT"]
        if shard == shard_count - 1:
            finalized_boundary = None if len(self.slots) - shard_count <= 0 else len(self.slots) - shard_count
            logging.info(f"finalized epoch boundary at {finalized_boundary}")
            dispatcher.send(signal="EPOCH_PUBLISHED", slots=self.slots, finalized_boundary=finalized_boundary)
