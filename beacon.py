import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii

EPOCH_TIME = 12

def beacon(shard_count):
    slots = []

    while True:
        time.sleep(EPOCH_TIME)
        for i in range(0, shard_count):
            logging.info(f"publishing beacon request for shard {i}")
            dispatcher.send(signal=f"BEACON_SHARD_{i}")
