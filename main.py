import gevent
from gevent.wsgi import WSGIServer

from gflib.utils.observer import Observer,FiredEvent
from gflib.utils.config import Config
from gflib.network.protocols import AMFProtocol,AMFDOTRouter,HTTPProtocol,HTTPDOTRouter
from gflib.network.rack import ServerRack

import time
import sys
import logging

    
class DaemonChild(object):
    """Main runner. Initialize all modules and start process loop"""
    def __init__(self,pnum=0):
        self.proc_num = pnum
        self.events = Observer()
        self.conf = Config.getInstance()
        
    def run(self):
        self._loop()    
        
    @classmethod
    def reload_config(cls):
        pass
       
    def _shutdown(self):
        logging.debug('Shuting down the daemon child.')
        sys.exit(0)

    def _loop(self):
        e = self.events.wait('shutdown')
        try:
            servers = []
            # use higher backlog for more concurency
            router   = AMFDOTRouter()
            protocol = AMFProtocol(router)
            servers.append(WSGIServer(
                     ('127.0.0.1',9001), 
                     protocol
                     ,backlog=4096
                     ,log=None
            ))
            
            router   = HTTPDOTRouter()
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
 

            
            
            
