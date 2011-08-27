from gflib.server.app import BaseApplication
from gflib.logging.logger import setupLogging
from gflib.utils.config import Config
from gflib.utils.observer import Observer

from main import DaemonChild

import logging
import yaml


class Application(BaseApplication):
    """Application class. Used for defining application as a module block which
    passed to the server for executing."""
 
    def run(self, pnum):
        """Executed on each process init"""
        try:
            # Main daemon child processes initializing here. 
            # Pnum is process number in stack
            d = DaemonChild(pnum)
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.stop()

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        logging.debug('startup')
    
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """             
        logging.debug('reload child')
            
    
    def shutdown(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """     
        logging.debug('kill child')
    

