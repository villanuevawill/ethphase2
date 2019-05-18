import logging
import threading
import time
import sys
from shard import shard
from pydispatch import dispatcher
from beacon import beacon
import matplotlib.pyplot as plt
from viz import VizController

SHARD_COUNT = None

if __name__ == "__main__":
    shard_count = int(sys.argv[1])
    SHARD_COUNT = shard_count
    
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    shard_signals = []
    viz = []
    for i in range(shard_count):
        logging.info(f"Main    : creating thread {i}")
        shard_signals.append(f"SHARD_{i}")
        viz.append(VizController(i))
        #threads.append(threading.Thread(target=viz, args=(i,)))
        threads.append(threading.Thread(target=shard, args=(i,shard_count,)))

    logging.info(f"Main    : shard signals {shard_signals}")

    for i, thread in enumerate(threads):
        logging.info(f"Main    : starting thread {i}")
        thread.start()

    logging.info("Main    : creating beacon chain")
    beacon_chain = threading.Thread(target=beacon, args=(SHARD_COUNT,))

    logging.info("Main    : starting beacon chain")
    beacon_chain.start()

    logging.info("Main    : all initialized...")
    
    figs=[]
    while True:
        for i in range(shard_count):
            figs.append(plt.figure(i))
            viz[i].render()
        plt.show()
    
    
    
    
        plt.clf()
    plt.imshow(frames[k],cmap=plt.cm.gray)
    fig.canvas.draw()
    time.sleep(1e-6)