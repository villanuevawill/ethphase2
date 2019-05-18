import logging
import threading
import time
import sys
from shard import shard
from pydispatch import dispatcher


def handle_event( sender ):
    """Simple event handler"""
    logging.info("Signal was sent by")

def beacon_chain():
    while True:
        logging.info("Beacon Chain Running")
        time.sleep(2)
        dispatcher.connect( handle_event, signal="SHARD_1", sender=dispatcher.Any )

if __name__ == "__main__":
    shard_count = int(sys.argv[1])
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    shard_signals = []

    for i in range(shard_count):
        logging.info(f"Main    : creating thread {i}")
        shard_signals.append(f"SHARD_{i}")
        threads.append(threading.Thread(target=shard, args=(i,)))

    logging.info(f"Main    : shard signals {shard_signals}")

    for i, thread in enumerate(threads):
        logging.info(f"Main    : starting thread {i}")
        thread.start()

    logging.info("Main    : creating beacon chain")
    beacon_chain = threading.Thread(target=beacon_chain)

    logging.info("Main    : starting beacon chain")
    beacon_chain.start()

    logging.info("Main    : all initialized...")
