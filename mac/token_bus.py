from mac.base import BaseMAC, simulation


class TokenBusMAC(BaseMAC):
    RETRANSMIT_LIMIT = 16 

    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs) 
    
    @simulation
    def transmit_packet(self, link, packet):
        # TODO: implement
        pass

    @simulation 
    def on_token_expired(self):
        # TODO: implement
        pass 