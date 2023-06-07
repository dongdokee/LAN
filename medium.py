from utils import MyLogger


logger = MyLogger() 


class TransmissionOnMedium:
    def __init__(self, src_id=None, start_time=None, end_time=None, collision_event=None):
        self.src_id = src_id 
        self.start_time = start_time 
        self.end_time = end_time 
        self.is_collision_occur = False 
        self.collision_event = collision_event


class Medium(object):
    BUSY_DELAY = 1e-6

    def __init__(self, env, node_list=None):
        self.env = env

        if node_list is None:
            self.node_list = []
        else:
            self.node_list = node_list 

        self.concurrent_tx_map = dict()

        self.busy_event = env.event()
        self.busy_event.succeed()

    @property 
    def name(self):
        return "Medium"

    def get_all_tx_at_time_t(self, t):
        result = []
        for tx in self.concurrent_tx_map.values():
            if t >= tx.start_time and t <= tx.end_time:
                result.append(tx) 

        return result 

    def is_busy_at_time_t(self, t):
        return self.get_all_tx_at_time_t(t) > 1 
    
    def wait_until_idle(self, wait_until_idle_event):
        if not self.busy_event.triggered:
            yield self.busy_event
        else:
            yield self.env.timeout(0.0)

    def delayed_busy(self):
        yield self.env.timeout(self.BUSY_DELAY)
        if not self.busy_event.triggered:
            return
         
        if len(self.get_all_tx_at_time_t(self.env.now)) > 1:
            self.busy_event = self.env.event()

    def access(self, tx_node_id, tx_time, tx_result_event, collision_event, stop_tx_event):
        tx = TransmissionOnMedium(src_id=tx_node_id, start_time=self.env.now, end_time=self.env.now + tx_time, collision_event=collision_event)
        tx_result = {"success": True, "reason": "success"} 
        self.concurrent_tx_map[tx_node_id] = tx

        if not self.busy_event.triggered:
            pass
        else:
            yield self.env.timeout(self.BUSY_DELAY) 
            if self.busy_event.triggered:
                self.busy_event = self.env.event() 

        concurrent_tx_list = self.get_all_tx_at_time_t(self.env.now)
        if len(concurrent_tx_list) > 1:
            for concurrent_tx in concurrent_tx_list:
                if not concurrent_tx.collision_event.triggered:
                    concurrent_tx.is_collision_occur = True 
                    concurrent_tx.collision_event.succeed(value=True)

        wait_tx = self.env.timeout(tx_time)
        tx.wait_in_medium_event = wait_tx 

        ret = yield wait_tx | stop_tx_event 

        if tx.is_collision_occur:
            tx_result["success"] = False 

            if wait_tx in ret:
                tx_result["reason"] = "충돌 발생 & 끝까지 전송"
            else:
                tx_result["reason"] = "충돌 발생 & 노드가 중단 요청" 
        else:
            collision_event.succeed(value=False)

        tx_result_event.succeed(value=tx_result)

        del self.concurrent_tx_map[tx_node_id]

        if not self.concurrent_tx_map and not self.busy_event.triggered:
            self.busy_event.succeed()

    def send_jamming_signal(self):
        for node in self.node_list:
            self.env.process(node.mac.on_receive_jamming_signal())


class WiredMedium(Medium):
    def __init__(self, env):
        super().__init__(env) 


class WirelessMedium(Medium):
    def __init__(self, env):
        super().__init__(env) 
