import logging
import os
import sys
import atexit
import yaml
import gevent
# internal ###########################
from gflib.utils.config import InitConfig
from gflib.server.daemon import Server
from gflib.utils.observer import Observer
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
        self.name = self.conf.get('AppName',None) or name or "GFDaemon"
        self.pidsdir = self.conf.get('server.pidsdir', '').rstrip('/ ')
        self.logging = self.conf.get('logging',{"error":None,"log":None})
        self.conf.set('pathes.base',os.path.dirname(os.path.abspath(sys.argv[0])))
        if root_path:
            self.conf.set('pathes.root',root_path)
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
        logging.debug('fire exit')
        atexit.register(self._exit_func_child)
        e = Observer()
        e.fire('shutdown')
                       
    def _exit_func_child(self):
        """Function called last in the shutdown queue of child process"""
        logging.debug('stop child')
        pidfile = self.pidsdir+'/gfchild_'+str(os.getpid())+'.pid'
        if os.path.exists(pidfile):
            os.remove(pidfile)
        logging.shutdown()
        self.shutdown()  
        
    def _reload_config(self):
        gevent.getcurrent()
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
            
        o = Observer()
        o.fire('reload_config')
        
    def _reload_child_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR1 signal. Used for configuration 
           reload without daemon restart.
        """      
        self._reload_config()
        self.reload_config()
        
    def _reload_daemon_config(self, sig=None, frame=None): 
        """It's executed when server get SIGUSR1 signal. Used for configuration 
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

