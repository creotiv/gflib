from gflib.server.app import BaseApplication
from gflib.logging.logger import setupLogging
from gflib.utils.config import Config
from gflib.utils.observer import Observer

from main import DaemonChild,MainDaemon

import logging
import atexit
import os
import sys
import gevent
import gc
import yaml


class Application(BaseApplication):
    """Application class. Used for defining application as a module block which
    passed to the server for executing."""
 
    def run_daemon(self, *args, **kwargs):
        """Executed on daemon init"""
        setupLogging()
        logging.debug('daemon '+str(Observer()))
        # Main daemon process initializing here
        try:
            d = MainDaemon()
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.stop_daemon()

    def run_process(self, pnum, *args, **kwargs):
        """Executed on each process init"""
        setupLogging(pnum)
        logging.debug('proc '+str(Observer()))
        try:
            # Main daemon child processes initializing here. 
            # Pnum is process number in stack
            d = DaemonChild()
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.stop_child()

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        pass
    
    def reload_daemon_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """      
        pass
    
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """             
        pass
            
    
    def shutdown_process(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """     
        pass
    
    def shutdown_daemon(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """        
        pass

