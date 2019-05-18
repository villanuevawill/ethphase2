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
            # When shard writes crosslink, we can update the next beacon block
            dispatcher.connect(self.handle_shard_write, signal=f"SHARD_TO_BEACON_{i}")

        while True:
            # wait epoch slot time before collecting next slot data
            time.sleep(system_config["EPOCH_SLOT_TIME"])

            # let shard know it needs to write its crosslink to the beacon chain
            current_slot = len(self.slots) % self.shard_count
            dispatcher.send(signal=f"BEACON_TO_SHARD_{current_slot}")

    def handle_shard_write(self, blocks, shard):
        self.slots.append(blocks)
        if shard == self.shard_count - 1:
            # send index of finalized boundary
            finalized_boundary = None if len(self.slots) - self.shard_count <= 0 else len(self.slots) - self.shard_count
            logging.info(f"finalized epoch boundary at {finalized_boundary}")
            dispatcher.send(signal="EPOCH_PUBLISHED", slots=self.slots, finalized_boundary=finalized_boundary)
