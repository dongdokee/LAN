from mac.csma import CSMA_MAC 
from mac.base import simulation 
import numpy as np 
from utils import MyLogger

logger = MyLogger() 


class CSMA_CD_MAC(CSMA_MAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

        self.backoff = False 

    @simulation
    def on_collision_detected(self, link, packet):
        # TODO: implement 
        pass 

    @simulation
    def on_receive_jamming_signal(self):
        # TODO: implement 
        pass 

    @simulation 
    def on_transmission_failed(self, link, packet, reason):
        # TODO: implement 
        pass 

    @simulation 
    def on_transmission_success(self, link, packet):
        # TODO: implement
        pass 