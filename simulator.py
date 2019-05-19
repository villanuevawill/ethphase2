import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii
from config import system_config


class Simulator():
    def __init__(self):
        self.shard_count = system_config["SHARD_COUNT"]
        self.account_delta = system_config["ACCOUNT_DELTA"]
        self.account_max = system_config["ACCOUNT_MAX"]
        self.state = []
        self.receipts = []

        for i in range(0, self.shard_count):
            self.state.append({})
            self.receipts.append([])

    def run(self):
        for i in range(0, self.shard_count):
            dispatcher.connect(self.generate_transactions, signal=f"SHARD_{i}")

    def generate_transactions(self, message, shard):
        self.state[shard] = message.state
        self.receipts[shard] = message.receipts

        shard_state = self.state[shard]
        receipts = message.receipts

        current_accounts = list(shard_state.keys())

        transactions = []
        for receipt in self.receipts[shard]:
            sender = receipt.receiver
            receiver = random.randint(0, self.account_max)
            cross_shard = random.random() > .8

            if cross_shard:
                random.seed(shard + message.slot)
                to_shard = random.randint(0, self.shard_count - 1)
            else:
                to_shard = shard

            random.seed(shard + message.slot)
            value = random.randint(0, receipt.value)
            transaction = {
                "sender": sender,
                "receiver": receiver,
                "shard": to_shard,
                "value": value,
                "witness": {
                    "receipt_id": receipt.id,
                    "sender": receipt.sender,
                    "receiver": receipt.receiver,
                    "shard": receipt.shard,
                    "value": receipt.value
                }
            }
            transactions.append(transaction)

        for i in range(0, 2):
            sender_address = random.choice(current_accounts)
            sender = shard_state[sender_address]
            receiver = random.randint(0, self.account_max)
            value = random.randint(0, sender.root_balance if not sender.state else sender.state.balance)
            sender.root_balance -= value
            to_shard = random.randint(0, self.shard_count - 1)

            transaction = {
                "sender": sender_address,
                "receiver": receiver,
                "value": value,
                "shard": to_shard,
                "witness": None,
            }
            transactions.append(transaction)

        for i in range(0, 4):
            sender_address = random.choice(current_accounts)
            sender = shard_state[sender_address]
            receiver = random.randint(0, self.account_max)
            value = random.randint(0, sender.root_balance)
            sender.root_balance = sender.root_balance - value

            transaction = {
                "sender": sender_address,
                "receiver": receiver,
                "value": value,
                "shard": shard,
                "witness": None
            }
            transactions.append(transaction)

        dispatcher.send(signal=f"TRANSACTIONS_{shard}", transactions=transactions)
