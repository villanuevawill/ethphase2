import logging
import time
from pydispatch import dispatcher
import random
import os
import binascii

SLOT_TIME = 2.9
ACCOUNT_DELTA = 5
state = []

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


# Global state
class State():
    def __init__(self):
        self.state = []

    def greedy_genesis_state(self):
        genesis_account = Account(None, [], 10000000)
        self.state.append(genesis_account)
        return state

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


def on_shard_update()


def shard(name, shard_count):
    shard_state = State()
    shard_state.greedy_genesis_state()
    dispatcher.connect( handle_specific_event, signal=, sender=dispatcher.Any )

    while True:
        transactions = shard_state.generate_random_transactions()
        block = {
            "root": new_hash(),
            "transactions": transactions,
            "state": shard_state.state
        }
        slots.append(block)
        dispatcher.send(signal=f"SHARD_{name}", message=block)
        logging.info(f"dispatched {block}")
        time.sleep(SLOT_TIME)
