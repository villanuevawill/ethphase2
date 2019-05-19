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

    def __repr__(self):
        return "[yes_dep: %r, no_deps: %r, balance: %d]" % (self.yes_dep, self.no_deps, self.balance)


class AccountState():
    def __init__(self, state, root_balance):
        self.state = state
        self.alt_states = []
        self.root_balance = root_balance


class Transaction():
    def __init__(self, sender, receiver, value):
        self.sender = sender
        self.receiver = receiver
        self.value = value

    def __repr__(self):
        return "[sender: %r, receiver: %r, balance: %d]" % (self.sender, self.receiver, self.balance)


class Receipt():
    def __init__(self, sender, receiver, value, shard):
        self.id = new_hash()
        self.sender = sender
        self.receiver = receiver 
        self.value = value
        self.shard = shard


class Block():
    def __init__(self, slot, root, transactions, receipts, state):
        self.slot = slot
        self.root = root
        self.transactions = transactions
        self.receipts = receipts
        self.state = state


# Global state
class State():
    def __init__(self):
        self.state = {}

    def greedy_genesis_state(self):
        genesis_account = AccountState(None, 10000000)
        self.state[0] = (genesis_account)
        return self.state


class Shard():
    def __init__(self, name):
        self.blocks = []
        self.pending_transactions = []
        self.state = State()
        self.receipts = []
        self.name = name

    def run(self):
        # Initiate with genesis account
        self.state.greedy_genesis_state()

        # Listens for a broadcast from the beacon chain that it is the shard's turn to write its crosslink
        dispatcher.connect(self.submit_to_beacon, signal=f"BEACON_TO_SHARD_{self.name}")

        # Listens for submitted transactions
        dispatcher.connect(self.accept_transactions, signal=f"TRANSACTIONS_{self.name}")

        while True:
            transactions = self.execute_transactions()

            # deep copy state so history is kept (vs. mutating state array)
            self.pending_transactions = []
            block = Block(len(self.blocks) - 1, new_hash(), transactions, copy.deepcopy(self.receipts), copy.deepcopy(self.state.state))
            self.receipts = []
            self.blocks.append(block)

            # notify visualizer and prediction market that a block has been submitted
            dispatcher.send(signal=f"SHARD_{self.name}", message=block, shard=self.name)
            logging.info(f"shard {self.name} dispatched block {block.root}")

            # wait slot period
            time.sleep(system_config["SHARD_SLOT_TIME"])

    def execute_transactions(self):
        transactions = []

        for pending_transaction in self.pending_transactions:
            transaction = self.execute_transaction(pending_transaction)
            transactions.append(transaction)
        return transactions


    def execute_transaction(self, transaction):
        needs_receipt = transaction["shard"] != self.name
        sender = transaction["sender"]
        receiver = transaction["receiver"]

        if not sender in self.state.state:
            new_account = AccountState(None, transaction["value"])
            self.state.state[sender] = new_account

        if transaction["witness"]:
            self.state.state[sender].root_balance += transaction["witness"]["value"]

        self.state.state[sender].root_balance -= transaction["value"]

        if (needs_receipt):
            receipt = Receipt(sender, receiver, transaction["value"], transaction["shard"])
            self.receipts.append(receipt)

            return transaction

        if receiver in self.state.state:
            self.state.state[receiver].root_balance += transaction["value"]
        else:
            new_account = AccountState(None, transaction["value"])
            self.state.state[receiver] = new_account

        return transaction


    def accept_transactions(self, transactions):
        self.pending_transactions = self.pending_transactions + transactions


    def submit_to_beacon(self):
        logging.info(f"shard {self.name} dispatching to beacon chain")
        block_roots = [block.root for block in self.blocks]
        dispatcher.send(signal=f"SHARD_TO_BEACON_{self.name}", blocks=block_roots, shard=self.name)
