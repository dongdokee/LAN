import simpy 
from packet import Packet 
from utils import MyLogger

logger = MyLogger() 


class Link(object):
    def __init__(self, env: simpy.Environment, medium, src: "Node", dst: "Node", link_speed: float):
        self.env = env
        self.medium = medium 
        self.src = src
        self.dst = dst 

        self.link_speed = link_speed 
        self.SLOT_TIME = 1 / (link_speed * 1e6) * 512
        # TODO: add latency 

    @property 
    def name(self):
        return f"링크(src={self.src.id_},dst={self.dst.id_})"


    def transmit(self, packet: Packet, tx_result_event, collision_event, stop_tx_event):
        tx_time = packet.packet_size * 8 / self.link_speed / 1e6

        tx_node_id = self.src.id_ 
        yield self.env.process(self.medium.access(tx_node_id, tx_time, tx_result_event, collision_event, stop_tx_event))
