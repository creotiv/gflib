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
        # Main daemon process initializing here
        try:
            d = MainDaemon()
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.shutdown_daemon()

    def run_process(self, pnum, *args, **kwargs):
        """Executed on each process init"""
        gc.enable()
        setupLogging(pnum)
        gevent.reinit()
        try:
            # Main daemon child processes initializing here. 
            # Pnum is process number in stack
            d = DaemonChild()
            d.run()
        except Exception,e:
            logging.exception('Error in main loop: %s' % e)
            self.shutdown_process()

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        pass
    
    def reload_daemon_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """      
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
            
        try:
            # Callback for additional signal handle at daemon and daemon children
            MainDaemon.reload_config()
        except Exception,e:
            logging.exception('config error: %s' % e)
    
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """ 
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
            
        try:
            # Callback for additional signal handle at daemon and daemon children
            DamonChild.reload_config()
        except Exception,e:
            logging.exception('config error: %s' % e)
            
    
    def shutdown_process(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """     
        # Register function called after shutdown
        atexit.register(self._exit_func)
        e = Observer()
        e.fire('shutdown')
                
    def _exit_func(self):
        """Function called last in the shutdown queue of child process"""
        conf = Config.getInstance()
        pidfile = conf.get('server.pidfile','')
        pid_path = os.path.join(*pidfile.split('/')[0:-1])
        pidfile = os.path.join(pid_path,'chpid_'+str(os.getpid())+'.pid')
        if os.path.exists(pidfile):
            os.remove(pidfile)
        logging.shutdown()
    
    def shutdown_daemon(self):
        """This method should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """        
        e = Observer()
        e.fire('shutdown')

