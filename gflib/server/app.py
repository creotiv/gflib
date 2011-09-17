import logging
import os
import sys
import atexit
import yaml
import gevent
# internal ###########################
from gflib.utils.config import Config
from gflib.server.daemon import Server
from gflib.utils.observer import Observer
###################################### 


class BaseApplication(object):
    """Application class. Used for defining application as a module block which
    passed to the server for executing."""

    def __init__(self,options=None):
        """
        Application initializing. Adding base path to os.path. Initialize logging.
        """
        if not options:
            raise Exception('Options not set.')
        self.options = dict(vars(options))
        
        self.name    = self.options.get('name',None) or "GFDaemon"
        self.pidsdir = self.options.get('pidsdir', 'pids').rstrip('/ ')
        chdir        = self.options.get('chdir', '').rstrip('/ ')
        if chdir:
            path     = {'root':chdir}
        else:
            path     = {'root':os.path.dirname(os.path.abspath(sys.argv[0]))}
        self.conf    = Config({'options':dict(self.options),'path':path}) 
        self._startup()
        
    def _startup(self):
        """It's executed before server startup. Used for initialize application 
           data.
        """
        self.startup()
        
    def _run_child(self, pnum, *args, **kwargs):
        self.run(pnum, *args, **kwargs)
 
    def _stop_daemon(self, sig=None, frame=None):
        """It's executed when server shutdown. Used for correct shutdown.
        """        
        pass

    def _stop_child(self, sig=None, frame=None):
        """It's executed when server shutdown. Used for correct shutdown.
        """     
        e = Observer()
        e.fire('shutdown')
        
    def _reload_config(self):
        o = Observer()
        o.fire('reload_config')
        
    def _reload_child_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR2 or SIGHUP signal. Used for configuration 
           reload without daemon restart.
        """      
        self._reload_config()
        self.reload_config()
        
    def _reload_daemon_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR2 or SIGHUP signal. Used for configuration 
           reload without daemon restart.
        """      
        self._reload_config()
        
    def stop(self):
        self._stop_child()

    def run(self, pnum, *args, **kwargs):
        """Executed on each process init"""
        pass

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        pass
    
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """      
        pass

    def shutdown(self):
        """This methon should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """        
        pass

