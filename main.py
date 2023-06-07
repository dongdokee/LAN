from world import WiredWorld 
from mac.non_csma import NonCSMA_MAC 
from mac.csma import CSMA_MAC
from mac.csma_cd import CSMA_CD_MAC 
from mac.token_bus import TokenBusMAC
import numpy as np 
import argparse 


def main(sim_time, num_nodes, packet_rate, packet_size, link_speed, expired_time, mac_cls):
    world = WiredWorld.create(num_nodes, packet_rate, packet_size, link_speed, expired_time, mac_cls)

    world.run(sim_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--time', default=60, required=False, type=float, help="시뮬레이션 시간")
    parser.add_argument('--numnodes', default=100, required=False, type=int, help="노드 개수")
    parser.add_argument('--packetrate', default=100, required=False, type=float, help="1초 당 보낼 패킷 개수")
    parser.add_argument('--packetsize', default=1500, required=False, type=int, help="패킷 사이즈 (byte)")
    parser.add_argument('--mac', default='no_csma', required=False, choices=['no_csma', 'csma', 'csma_cd', 'token_bus'])
    parser.add_argument('--linkspeed', default=1, required=False)
    
    args = parser.parse_args() 

    sim_time = args.time
    num_nodes = args.numnodes
    packet_rate = args.packetrate 
    packet_size = args.packetsize
    mac_alg = args.mac 
    link_speed = args.linkspeed

    if mac_alg == "token_bus":
        expired_time = 1e-3
    else:
        expired_time = None 

    if mac_alg == 'no_csma':
        mac_cls = NonCSMA_MAC
    elif mac_alg == 'csma':
        mac_cls = CSMA_MAC
    elif mac_alg == 'csma_cd':
        mac_cls = CSMA_CD_MAC 
    else:
        mac_cls = TokenBusMAC

    np.random.seed(1111) 

    main(sim_time, num_nodes, packet_rate, packet_size, link_speed, expired_time, mac_cls)
