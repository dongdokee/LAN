import simpy 
from utils import MyLogger
from packet import Packet 
from typing import List 
from link import Link 
from traffic_generator import TrafficGenerator



logger = MyLogger() 


class Node(object):
    def __init__(self, id_: int, env: simpy.Environment, medium, mac_cls):
        self.id_ = id_ 
        self.env = env
        self.medium = medium 

        self.token = None 
        self.next_node = None 
        self.acquire_token_event = None 

        self.queue = []
        self.link_map = dict() 
        self.traffic_generator = None 
        self.mac = mac_cls(env, self)
        
        self.new_packet_event = None 
        self.tx_result_event = None 
        self.collision_event = None 
        self.stop_tx_event = None 

        self.token_passing_event = None 
        logger.info(env.now, self.name, f"생성됨")

        # 통계
        self.tx_count = 0 
        self.tx_packet_count = 0
        self.rx_packet_count = 0
        self.tx_success_count = 0
        self.tx_success_packet_count = 0
        self.tx_fail_count = 0 
        self.retransmit_count = 0
        self.tx_collision_count = 0 
        self.tx_bytes = 0
        self.rx_bytes = 0 

    @property 
    def name(self):
        return f"노드(id={self.id_})" 
    
    # 노드 설정
    def configure_links(self, node_list: List["Node"], link_speed):
        for dst in node_list:
            if self.id_ != dst.id_:
                link = Link(self.env, self.medium, self, dst, link_speed)
                self.link_map[dst.id_] = link 

    def configure_traffic_generator(self, packet_rate, packet_size): 
        self.traffic_generator = TrafficGenerator(self.env, self, packet_rate, packet_size)

    # 토큰 패스 관련
    def configure_next_node(self, next_node):
        self.next_node = next_node 

    def run(self):
        while True:
            while self.queue:
                link, packet = self.queue.pop(0)

                logger.info(self.env.now, self.name, f"{link.dst.name}으로 보내는 {packet.name} 전송 개시")

                if not self.token_passing_event or self.token_passing_event.triggered:
                    self.token_passing_event = self.env.event() 

                self.mac.init_transmit()
                yield self.env.process(self.mac.transmit_packet(link, packet))
                self.mac.finish_transmit() 

                if not packet.success:
                    self.tx_packet_count -= 1 

                self.token_passing_event.succeed() 

            self.new_packet_event = self.env.event() 
            yield self.new_packet_event 

    def add_packet(self, link: Link, packet: Packet):
        self.queue.append((link, packet)) 
        if not self.new_packet_event.triggered:
            self.new_packet_event.succeed() 

    def has_token(self):
        return self.token is not None

    def wait_until_token_received(self):
        if not self.has_token():
            self.acquire_token_event = self.env.event() 

            yield self.acquire_token_event 

    def pass_token(self):
        logger.info(self.env.now, self.name, "토큰 상실")
        expired_time = self.token['expired_time']
        self.token = None 

        if self.token_passing_event and not self.token_passing_event.triggered:
            yield self.token_passing_event

        yield self.env.process(self.next_node.acquire_token(expired_time))

    def acquire_token(self, expired_time=None):
        if not expired_time:
            yield self.env.timeout(0.0) 
            return 

        logger.info(self.env.now, self.name, "토큰 획득")
        self.token = {'expired_time': expired_time}

        if self.acquire_token_event and not self.acquire_token_event.triggered:
            self.acquire_token_event.succeed() 

        yield self.env.timeout(expired_time)
        yield self.env.process(self.mac.on_token_expired()) 


    """
    매체에 접근하는 메소드
    """
    def transmit(self, link: Link, packet: Packet): 
        self.tx_result_event = self.env.event() 
        self.collision_event = self.env.event() 
        self.stop_tx_event = self.env.event() 

        if self.mac.tx_attempt <= 1:
            self.update_transmit(link, packet)
        else: 
            self.update_retransmit(link, packet) 
        self.env.process(link.transmit(packet, self.tx_result_event, self.collision_event, self.stop_tx_event))

        collision = yield self.collision_event

        if collision == True:
            self.update_collision() 
            yield self.env.process(self.mac.on_collision_detected(link, packet))

        tx_result = yield self.tx_result_event

        if tx_result["success"]:
            self.update_success_tx(link, packet) 
            yield self.env.process(self.mac.on_transmission_success(link, packet))
        else:
            reason = tx_result['reason']
            self.update_fail_tx(link, packet, reason)
            yield self.env.process(self.mac.on_transmission_failed(link, packet, reason))

    def wait_until_idle(self):
        yield self.env.process(self.medium.wait_until_idle(None))

    def stop_transmit(self):
        if self.stop_tx_event and not self.stop_tx_event.triggered:
            self.stop_tx_event.succeed()

        yield self.env.timeout(0.32 * 1e-6) 

    def send_jamming_signal(self):
        yield self.env.process(self.medium.send_jamming_signal())

    """
    결과 및 통계 관련 메소드 
    """
    def update_success_tx(self, link, packet):
        logger.info(self.env.now, self.name, f"{link.src.id_} to {link.dst.id_} {packet.name} success")
        self.tx_success_packet_count += 1 
        self.tx_success_count += 1 
        self.tx_bytes += packet.packet_size 
        link.dst.rx_packet_count += 1 
        link.dst.rx_bytes += packet.packet_size  
        packet.success = True 

        logger.info(self.env.now, self.name, f"{packet.name} 전송 성공, {self.tx_success_count} {self.tx_bytes}")

    def update_fail_tx(self, link, packet, reason):
        self.tx_fail_count += 1

        # logging
        logger.info(self.env.now, self.name, f"{packet.name} 전송 실패, 이유: {reason}")

    def update_transmit(self, link, packet):
        self.tx_packet_count += 1 
        self.tx_count += 1

    def update_collision(self):
        self.tx_collision_count += 1 

    def update_retransmit(self, link, packet):
        self.tx_count += 1 
        self.retransmit_count += 1

    def get_statistics(self):
        return {
            "tx_count": self.tx_count, 
            "tx_packet_count": self.tx_packet_count,
            "rx_packet_count": self.rx_packet_count, 
            "tx_success_count": self.tx_success_count,
            "tx_success_packet_count": self.tx_success_packet_count,
            "tx_fail_count": self.tx_fail_count,
            "retransmit_count": self.retransmit_count,
            "tx_collision_count": self.tx_collision_count,
            "tx_success_rate": 1.0 if self.tx_count == 0 else self.tx_success_count / self.tx_count,
            "packet_delivery_rate": 1.0 if self.tx_packet_count == 0 else float(self.tx_success_packet_count) / self.tx_packet_count,
            "tx_throughput": self.tx_bytes / self.env.now,
            "tx_bytes": self.tx_bytes,
            "rx_bytes": self.rx_bytes
        }
 

class WiredNode(Node):
    def __init__(self, id_, env, medium, mac_cls):
        super().__init__(id_, env, medium, mac_cls) 
