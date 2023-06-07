import numpy as np 
import simpy 
from typing import List 
from utils import MyLogger 
from link import Link 
from packet import Packet 


logger = MyLogger()


class TrafficGenerator(object):
    def __init__(self, env: simpy.Environment, node: "Node", packet_rate: float, packet_size: int=1500):
        self.env = env 
        self.node = node 
        self.packet_rate = packet_rate
        self.packet_size = packet_size

        self.current_packet_id = 0 

        logger.info(env.now, self.name, "생성됨")

    @property 
    def name(self):
        return f"트래픽 생성기(id={self.node.id_})"

    def run(self): 
        while True:
            arrival_time = np.random.exponential(1/self.packet_rate) 

            #arrival_time = 1 

            yield self.env.timeout(arrival_time)

            link = np.random.choice(list(self.node.link_map.values())) 
            packet = Packet(
                id_=self.current_packet_id, 
                packet_size=self.packet_size
            )

            self.node.add_packet(link=link, packet=packet)
            #logger.info(self.env.now, self.name, f"{link.dst.name}으로 보내는 {packet.name} 생성")

            self.current_packet_id += 1 
