import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii
import copy
import threading
from threading import Timer
from config import system_config


ACCOUNT_DELTA = 5

def new_hash():
    return binascii.hexlify(os.urandom(4)).decode('utf-8')

# Account state record
class Account():
    def __init__(self, yes_dep, no_deps, balance):
        # This state is conditional on this dependency being CORRECT
        self.yes_dep = yes_dep
        # This state is conditional on these dependencies being INCORRECT
        self.no_deps = no_deps
        # Account balance
        self.balance = balance
        self.root_balance = balance

    def __repr__(self):
        return "[yes_dep: %r, no_deps: %r, balance: %d]" % (self.yes_dep, self.no_deps, self.balance)


class Transaction():
    def __init__(self, sender, receiver, balance):
        self.sender = sender
        self.receiver = receiver
        self.balance = balance
    def __repr__(self):
        return "[sender: %r, receiver: %r, balance: %d]" % (self.sender, self.receiver, self.balance)


class Block():
    def __init__(self, slot, root, transactions, state):
        self.slot = slot
        self.root = root
        self.transactions = transactions
        self.state = state


# Global state
class State():
    def __init__(self):
        self.state = []

    def greedy_genesis_state(self):
        genesis_account = Account(None, [], 10000000)
        self.state.append(genesis_account)
        return self.state

    def generate_random_transactions(self):
        transactions = []
        accounts_length = len(self.state)
        account_set = accounts_length + ACCOUNT_DELTA
        self.state = self.state + ([None] * ACCOUNT_DELTA)

        for i in range(ACCOUNT_DELTA):
            sender_idx = random.randint(0, accounts_length - 1)
            receiver_idx = random.randint(0, account_set - 1)
            if sender_idx != receiver_idx:
                sender = self.state[sender_idx]

                if not sender:
                    continue

                transaction_amount = random.randint(1, sender.balance)
                transaction = Transaction(sender_idx, receiver_idx, transaction_amount)
                receiver = self.state[receiver_idx] or Account(None, [], 0) 
                sender.balance -= transaction_amount
                receiver.balance += transaction_amount
                self.state[receiver_idx] = receiver
                transactions.append(transaction)
        return transactions

class Shard():
    def __init__(self, name):
        self.blocks = []
        self.state = State()
        self.name = name

    def run(self):
        self.state.greedy_genesis_state()
        beacon_submit_stub = threading.Thread(target=self.submit_to_beacon)
        beacon_submit_stub.start()
        dispatcher.connect(self.submit_to_beacon, signal=f"BEACON_TO_SHARD_{self.name}")

        while True:
            transactions = self.state.generate_random_transactions()
            block = Block(len(self.blocks) - 1, new_hash(), transactions, copy.deepcopy(self.state.state))
            self.blocks.append(block)
            dispatcher.send(signal=f"SHARD_{self.name}", message=block)
            logging.info(f"dispatched {block}")
            time.sleep(system_config["SHARD_SLOT_TIME"])

    def submit_to_beacon(self):
        logging.info(f"shard {self.name} dispatching to beacon chain")
        block_roots = [block.root for block in self.blocks]
        dispatcher.send(signal=f"SHARD_TO_BEACON_{self.name}", blocks=block_roots, shard=self.name)
