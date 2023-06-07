from node import WiredNode
from medium import Medium, WiredMedium
import simpy 
from typing import List
from utils import convert_capacity, convert_throughput
import csv


class WiredWorld:
    def __init__(self, env: simpy.Environment, medium: Medium=None, node_list: List[WiredNode]=None):
        self.env = env 
        self.medium = medium 
        self.node_list = node_list 

    @classmethod 
    def create(cls, num_nodes: int, packet_rate: float, packet_size: int, link_speed: float, expired_time: float, mac_cls):
        env = simpy.Environment() 

        medium = WiredMedium(env) 

        node_list = [WiredNode(id_=i, env=env, medium=medium, mac_cls=mac_cls) for i in range(num_nodes)]
        medium.node_list = node_list 

        for i, node in enumerate(node_list):
            node.configure_links(node_list, link_speed) 
            node.configure_traffic_generator(packet_rate, packet_size)

            if i == len(node_list) - 1:
                node.configure_next_node(node_list[0])
            else:
                node.configure_next_node(node_list[i+1])

        env.process(node_list[0].acquire_token(expired_time))

        return cls(env, medium, node_list)

    def run(self, sim_time):
        for node in self.node_list:
            self.env.process(node.traffic_generator.run())
            self.env.process(node.run()) 

        self.env.run(until=sim_time) 

        packet_delivery_rate_acc = 0
        tx_throughput_aggregated = 0 
        for node in self.node_list:
            statistic = node.get_statistics() 

            packet_delivery_rate_acc += statistic['packet_delivery_rate']
            tx_throughput_aggregated += statistic['tx_throughput']

            print(node.name, statistic)

        print('네트워크 처리량 (Mbps)', convert_throughput(tx_throughput_aggregated))
        mean_pdr = packet_delivery_rate_acc / len(self.node_list) 
        print('평균 패킷전달률 (%)', mean_pdr * 100)
        
        