from amf import AMFProtocol
from http import HTTPProtocol
from socketio import SocketIOProtocol

class NoProtocolException(Exception):
    pass

def get_protocol(name):
    name = name.lower()
    if name == "amf":
        return AMFProtocol
    if name == "http":
        return HTTPProtocol
    if name == "socket.io":
        return SocketIOProtocol
        
    
    raise NoProtocolException('Protocol %s is not supported.' % name.upper())
