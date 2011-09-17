from gflib.server.app import BaseApplication
from gflib.logging.logger import setupLogging
from gflib.utils.config import Config
from gflib.utils.observer import Observer

from main import DaemonChild

import logging
import yaml
import os


class Application(BaseApplication):
    """Application class. Used for defining application as a module block which
    passed to the server for executing."""
 
    def run(self, pnum, *args, **kwargs):
        """Executed on each process init"""
        try:
            # Main daemon child processes initializing here. 
            # Pnum is process number in stack
            d = DaemonChild(pnum, kwargs.get('sockets',None))
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.stop()

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        logging.debug('startup')
        self.conf_path = self.conf.get('pathes.root')+'/conf/config.yaml'
        self.reload_config()
    
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """             
        logging.debug('reload child')
        try:
            stream = file(self.conf_path, 'r')
            data = yaml.load(stream)
            stream.close()
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                logging.error("Config error at position: (%s:%s)" % 
                                                    (mark.line+1, mark.column+1)
                )
        else:
            logging.debug('Configuration reloaded #%s' % os.getpid())
        if not data:
            data = {}
        self.conf.reinit(data)
            
    
    def shutdown(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """     
        logging.debug('kill child')
    

