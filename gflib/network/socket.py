import socket
import _socket

def send_data(conn=None,data='',buff=256):
    if isinstance(conn,tuple) or isinstance(conn,list):
        if isinstance(conn,list):
            conn = tuple(conn)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(conn)
        conn = s
    conn.send(data)
    res = ''
    while True:
        line = conn.recv(buff)
        res += line
        if not line or len(line)<buff: break
    return res
    
def create_socket(s, backlog=256, reuse_addr=None):
    if s[0] == 'tcp':
        family  = _socket.AF_INET
        type    = _socket.SOCK_STREAM
        proto   = _socket.getprotobyname('tcp')
    elif s[0] == 'unix':
        family  = _socket.AF_UNIX
        type    = _socket.SOCK_STREAM
        proto   = _socket.getprotobyname('unix')
    elif s[0] == 'udp':
        family  = _socket.AF_INET
        type    = _socket.SOCK_DGRAM
        proto   = _socket.getprotobyname('udp')
    
    sock = _socket.socket(family=family,type=type,proto=proto)
    if reuse_addr is not None:
        sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, reuse_addr)
    sock.bind((s[1],int(s[2])))
    sock.listen(backlog)
    sock.setblocking(0)
    return sock
