from gflib.network.protocols.base import BaseProtocol

class SocketIOProtocol(BaseProtocol):    
    """
        SocketIO Protocol
    
    """
    def init(self,*args,**kvargs):
        self.handler = self.base_handler
    

