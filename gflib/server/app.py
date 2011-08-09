import logging
import os
import sys
import yaml
# internal ###########################
from gflib.config import InitConfig
from gflib.server.daemon import Server
###################################### 

class BaseApplication(object):
    """Application class. Used for defining application as a module block which
    passed to the server for executing."""

    def __init__(self,name=None,conf_path=None,root_path=None):
        """
        Application initializing. Adding base path to os.path. Initialize logging.

        @type name: C{str}
        @param name: Application name. That will be seen in 'top' console.                

        @type conf_path: C{str}
        @param conf_path: Path to the config file. Absolute or relative.                

        @type conf_path: C{str}
        @param conf_path: Path to the application root.                

        """
        self.conf_path = conf_path or 'config.yaml'
        self.conf = InitConfig(path=self.conf_path)
        self.name = self.conf.get('AppName',None) or name or "tor"
        self.pidfile = self.conf.get('server.pidfile', 'tor.pid')
        self.logging = self.conf.get('logging',{"error":None,"log":None})
        self.conf.set('pathes.base',os.path.dirname(os.path.abspath(sys.argv[0])))
        if root_path:
            self.conf.set('pathes.root',root_path)
        self.startup()
 
    def run_daemon(self, *args, **kwargs):
        """Executed on daemon init"""
        pass

    def run_process(self, pnum, *args, **kwargs):
        """Executed on each process init"""
        pass

    def startup(self):
        """This methon should be rewrited in subclass. It's executed before 
        server startup. Used for initialize application data.
        """
        pass
    
    def _stop_daemon(self, sig=None, frame=None):
        """It's executed when server shutdown. Used for correct shutdown.
        """        
        server = Server.instance()
        server.stop()
        self.shutdown_daemon()

    def _stop_procces(self, sig=None, frame=None):
        """It's executed when server shutdown. Used for correct shutdown.
        """        
        self.shutdown_process()  
        
    def _reload_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR1 signal. Used for configuration 
           reload without daemon restart.
        """      
        self.reload_config()
        
    def reload_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """      
        pass
    
    def reload_daemon_config(self):
        """This methon should be rewrited in subclass. It's executed when server 
           get SIGUSR1 signal. Used for configuration reload without daemon restart.
        """      
        pass
        
    def _reload_daemon_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR1 signal. Used for configuration 
           reload without daemon restart.
        """      
        server = Server.instance()
        server.reload_child_configs()
        self.reload_daemon_config()

    def shutdown_process(self):
        """This methon should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """        
        pass

    def shutdown_daemon(self):
        """This methon should be rewrited in subclass. It's executed after 
        server shutdown. Used for correct shutdown.
        """        
        pass

