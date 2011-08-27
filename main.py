import gevent
from gevent.wsgi import WSGIServer

from gflib.utils.observer import Observer,FiredEvent
from gflib.utils.config import Config
from gflib.network.protocols import (AMFProtocol,AMFDOTRouter,HTTPProtocol,
                                     HTTPDOTRouter,DistributedHTTPDOTRouter)
from gflib.network.distribution import Network
from gflib.network.rack import ServerRack

import time
import os,sys
import logging
from gevent_zeromq import zmq
    
class DaemonChild(object):
    """Main runner. Initialize all modules and start process loop"""
    def __init__(self,pnum):
        self.proc_num = pnum
        self.events = Observer()
        self.conf = Config.getInstance()
        
    def run(self):
        logging.debug(self.proc_num)
        if self.proc_num == 0:    
            self._main_loop()
        elif self.proc_num == 1:
            self._broker_loop()
        elif self.proc_num > 1:
            self._worker_loop()
        
        
    @classmethod
    def reload_config(cls):
        pass
       
    def _shutdown(self):
        logging.debug('Shuting down the daemon child.')
        sys.exit(0)
        
    def _broker_loop(self):
        context = zmq.Context()
        frontend = context.socket(zmq.XREP)
        backend = context.socket(zmq.XREQ)
        frontend.bind("tcp://*:5559")
        backend.bind("tcp://*:5560")

        # Initialize poll set
        poller = zmq.Poller()
        poller.register(frontend, zmq.POLLIN)
        poller.register(backend, zmq.POLLIN)

        # Switch messages between sockets
        while True:
            socks = dict(poller.poll())

            if socks.get(frontend) == zmq.POLLIN:
                message = frontend.recv()
                more = frontend.getsockopt(zmq.RCVMORE)
                if more:
                    backend.send(message, zmq.SNDMORE)
                else:
                    backend.send(message)

            if socks.get(backend) == zmq.POLLIN:
                message = backend.recv()
                more = backend.getsockopt(zmq.RCVMORE)
                if more:
                    frontend.send(message, zmq.SNDMORE)
                else:
                    frontend.send(message)

    def _main_loop(self):
        e = self.events.wait('shutdown')
        try:
            servers = []
            spool = [
                'tcp://127.0.0.1:5559'
            ]
            # use higher backlog for more concurency
            """router   = AMFDOTRouter()
            protocol = AMFProtocol(router)
            servers.append(WSGIServer(
                     ('127.0.0.1',9001), 
                     protocol
                     ,backlog=4096
                     ,log=None
            ))"""
            
            router   = DistributedHTTPDOTRouter(servers=spool,iopool=20)
            #router   = HTTPDOTRouter()
            protocol = HTTPProtocol(router)
            servers.append(WSGIServer(
                     ('127.0.0.1',9002), 
                     protocol
                     ,backlog=4096
                     ,log=None
            ))
            rack = ServerRack(servers).serve_forever()
            
        except KeyboardInterrupt:
            self._shutdown()
        except FiredEvent:
            self._shutdown()
        except MemoryError:
            logging.error('--------!!!!!!!MemoryError!!!!!!!--------')
            self._shutdown()
        finally:
            e.cancel()
            
        
    def _worker_loop(self):
        e = self.events.wait('shutdown')
        try:
            spool = [
                'tcp://127.0.0.1:5560'
            ]
            dp = DistributedHTTPDOTRouter(servers=spool,iopool=200)
            dp.serve_forever()
        except KeyboardInterrupt:
            self._shutdown()
        except FiredEvent:
            self._shutdown()
        except MemoryError:
            logging.error('--------!!!!!!!MemoryError!!!!!!!--------')
            self._shutdown()
        finally:
            e.cancel()
 

            
            
            
