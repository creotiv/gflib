import socket

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
