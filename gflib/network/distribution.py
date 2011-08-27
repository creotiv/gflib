from gevent_zeromq import zmq
from gflib.utils import json_encode,json_decode
from gflib.utils.ObjectFactory import ObjectFactory
from gevent.queue import PriorityQueue

import time
import logging

class Network(object):

    def __new__(cls,size=5,ntype='REQ',servers=None,iopool=1):
        if not hasattr(cls,'_instance'):
            cls._instance = object.__new__(cls)
            cls._instance.size      = size
            cls._instance.ntype     = ntype
            cls._instance.servers   = servers
            cls._instance.iopool    = iopool
            cls._instance.queue     = PriorityQueue(size)
            cls._instance.context   = zmq.Context(iopool)
            for x in xrange(size):
                try:
                    socket = None
                    if ntype == 'REQ':
                        socket = cls._instance.context.socket(zmq.REQ)
                        for server in servers:
                            socket.connect(server)
                    elif ntype == 'REP':
                        socket = cls._instance.context.socket(zmq.REP)
                        for server in servers:
                            socket.bind(server)
                    elif ntype == 'REP2':
                        socket = cls._instance.context.socket(zmq.REP)
                        for server in servers:
                            socket.connect(server)
                    
                    cls._instance.queue.put(
                        (time.time(),socket)
                    )
                except Exception,e:
                    logging.exception(e)
                    raise Exception('Can\'t create zeromq socket: %s' % e)
                    
        return cls._instance     
        
    def get_socket(self,block=True,timeout=None):
        return NetworkSocket(self,self.queue.get(block,timeout)[1])


class NetworkSocket(object):

    __slots__ = ['socket','pool']

    def __init__(self,pool,socket):
        self.pool           = pool
        self.socket         = socket
    
    def send(self,msg):
        try:
            msg = json_encode(msg)
        except Exception,e: 
            logging.exception('JSON ERROR: %s ' % e)
        self.socket.send(msg)
            
    def recv(self):
        return json_decode(self.socket.recv())
        
    def __del__(self):
        logging.debug('BACK IN POOL')
        self.pool.queue.put((time.time(),self.socket))
        del self.pool
        del self.conn
        

        
