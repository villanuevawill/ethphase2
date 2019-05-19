import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii
from config import system_config


class Prediction():
    def __init__(self):
        self.predictions = []
        self.finalizations = []
        self.shard_count = system_config["SHARD_COUNT"]
        for i in range(0, self.shard_count):
            self.predictions.append([])

    def run(self):
        for i in range(0, self.shard_count):
            dispatcher.connect(self.update_shard_predictions, signal=f"SHARD_{i}")

    def update_shard_predictions(self, message, shard):
        shard_predictions = self.predictions[shard]
        shard_predictions.append(message)
