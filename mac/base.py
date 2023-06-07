from utils import MyLogger
import types 


logger = MyLogger() 


def simulation(method):
    def to_generator(mac, *args, **kwargs):
        result = method(mac, *args, **kwargs)

        if isinstance(result, types.GeneratorType):
            return result 
        else:
            def wrapper(env, result):
                yield env.timeout(0.0) 
                
                return result 
            return wrapper(mac.env, result)
    
    return to_generator 



class BaseMAC:
    RETRANSMIT_LIMIT = 16 

    def __init__(self, env, node, *args, **kwargs):
        self.env = env 
        self.node = node
        self.tx_attempt = 0 
        self.is_transmitting = False
    
    def init_transmit(self):
        self.tx_attempt = 0

        self.is_transmitting = True

    def finish_transmit(self):
        self.tx_attempt = 0 

        self.is_transmitting = False 
    
    @simulation
    def transmit_packet(self, link, packet):
        self.tx_attempt += 1

        if self.tx_attempt > self.RETRANSMIT_LIMIT:
            yield self.env.timeout(0.0) 
        else:
            yield self.env.process(self.node.transmit(link, packet)) 

    @simulation
    def on_collision_detected(self, link, packet):
        pass 

    @simulation
    def on_receive_jamming_signal(self, link, packet):
        pass 

    @simulation 
    def on_transmission_failed(self, link, packet, reason):
        yield self.env.process(self.transmit_packet(link, packet))

    @simulation 
    def on_transmission_success(self, link, packet):
        pass 
