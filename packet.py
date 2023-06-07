

class Packet:
    def __init__(self, id_: int, packet_size: int):
        self.id_ = id_
        self.packet_size = packet_size 
        self.success = False 
 
    @property 
    def name(self):
        return f"패킷(id={self.id_})"
    