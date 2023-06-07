from mac.csma import CSMA_MAC 
from mac.base import simulation 


class CSMA_CD_MAC(CSMA_MAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

    @simulation
    def transmit_packet(self, link, packet):
        # TODO: implement
        pass 