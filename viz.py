import logging
import networkx as nx
import matplotlib.pyplot as plt
from pydispatch import dispatcher

      
class VizController():
    def __init__(self, num):
        self.G = nx.MultiDiGraph()
        self.signal=f"SHARD_{num}"
        self.transactions = []
        self.states = []
        dispatcher.connect( self.handle_event, signal=self.signal, sender=dispatcher.Any )
        
    def handle_event(self, sender, message ):
        logging.info(f"received block: {message}")
        self.addStates(message['state'])
        self.addTransactions(message['transactions'])
                
    def addStates(self,states):
        for i in range(len(states)):
            if states[i] is not None:
                logging.info(f"adding state: {states[i]}")
                self.G.add_node(i)
    def addTransactions(self,transactions):
        logging.info(f"adding transactions: {transactions}")
        for t in transactions:
            self.G.add_edge(*(t.sender,t.receiver))
        
    def render(self):
        nx.draw(self.G)
        
        
        
if __name__ == "__main__":
    controller = VizController(0)
    controller.render()
    