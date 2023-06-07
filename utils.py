import logging 
import datetime 
import os 

class SingletonType(type):
    _instances = {} 

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls] 
    

class MyLogger(object, metaclass=SingletonType):
    _logger = None 

    def __init__(self):
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG) 

        now = datetime.datetime.now()
        dirname = './log'

        if not os.path.isdir(dirname):
            os.mkdir(dirname) 

        fileHandler = logging.FileHandler(dirname + "/log_" + now.strftime("%Y-%m-%d") + ".log", mode="w")

        streamHandler = logging.StreamHandler() 

        self._logger.addHandler(fileHandler)
        self._logger.addHandler(streamHandler)

    def get_logger(self):
        return self._logger 
    
    def info(self, t, subject, msg):
        self._logger.info(f"[{t:6.8f}] [{subject}] {msg}")


def convert_throughput(bps_in_float: float) -> str:
    mbps = bps_in_float / 1e6 

    return f"{mbps:10.2f}" + ' Mbps'

def convert_capacity(bytes: float) -> str:
    mb = bytes / 1e6 

    return f"{mb:10.2f}" + ' MB'