import gevent

from gflib.utils.observer import Observer,FiredEvent
from gflib.utils.config import Config

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
            while True:
                logging.debug('child loop '+str(time.time()))
                gevent.sleep(5)
        except KeyboardInterrupt:
            self._shutdown()
        except FiredEvent:
            self._shutdown()
        except MemoryError:
            logging.error('--------!!!!!!!MemoryError!!!!!!!--------')
            self._shutdown()
        finally:
            e.cancel()
 
class MainDaemon(object):
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
        logging.debug('Shuting down the Main daemon.')
        sys.exit(0)

    def _loop(self):
        e = self.events.wait('shutdown')
        try:
            while True:
                logging.debug('daemon loop '+str(time.time()))
                gevent.sleep(5)
        except KeyboardInterrupt:
            self._shutdown()
        except FiredEvent:
            self._shutdown()
        except MemoryError:
            logging.error('--------!!!!!!!MemoryError!!!!!!!--------')
            self._shutdown()
        finally:
            e.cancel()
            
            
            
