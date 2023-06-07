from mac.base import BaseMAC, simulation
from utils import MyLogger


logger = MyLogger() 


class NonCSMA_MAC(BaseMAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

    @simulation
    def transmit_packet(self, link, packet):
        # TODO: implement 
        pass 

    @simulation 
    def on_transmission_failed(self, link, packet, reason):
        # TODO: implement 
        pass 