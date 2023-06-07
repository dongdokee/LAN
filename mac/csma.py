from mac.non_csma import NonCSMA_MAC
from mac.base import simulation 
from utils import MyLogger

logger = MyLogger() 



class CSMA_MAC(NonCSMA_MAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

    @simulation
    def transmit_packet(self, link, packet):
        # TODO: implement 
        pass 