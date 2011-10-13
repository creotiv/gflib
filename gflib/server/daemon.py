import sys
import os
import os.path
import time
import signal
import logging
import socket
import gevent
from gevent.event import Event

# internal ########################### 
from gflib.utils import set_proc_name, get_somaxconn
from gflib.logging.logger import setupLogging
from gflib.network.socket import create_socket
###################################### 

if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

class Daemon(object):

    def __init__(self,options=None):

        self.uid         = options.get('uid',None)
        self.gid         = options.get('gid',None)
        self.chdir       = options.get('chdir',None)
        self.processes   = options.get('proc_num',None) or 1
        self.pidsdir     = options.get('pidsdir',None).rstrip('/ ') or 'pids'
        self.debug       = options.get('debug',None)
        self.logs_dir    = options.get('logdir',None)
        self.logs_count  = options.get('logfiles',None)
        self.logs_size   = options.get('logsize',None)
        self.backlog     = options.get('backlog',None)
        self.sockets     = options.get('sockets','')
        self.children    = []
        self.stop_signal = False
        self.pid         = 0
        
       
    def _daemonize(self):
        """
        Standard daemonization of a process.
        http://www.svbug.com/documentation/comp.unix.programmer-FAQ/faq_2.html#SEC16
        """
        if gevent.fork():
            os._exit(0)

        os.setsid()
        if gevent.fork():
            os._exit(0)

        os.umask(0)
        
        if self.chdir:        
            os.chdir(self.chdir)

        """sys.stdout.flush()
        sys.stderr.flush()
        si = file('/dev/null', 'r')
        so = file('logs/console.log', 'a+')
        se = file('logs/console.log', 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        """
        for i in xrange(3):
            # Closing parent standart in,out,error fd's
            os.close(i)
            
        os.open(REDIRECT_TO, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)
        
        if self.uid:
            os.setuid(self.uid)
        if self.gid:
            os.setgid(self.gid)
            
        self.pid = os.getpid()
        file(self.pidsdir+'/gfdaemon.pid','w+').write(str(self.pid))
    
    def _init_logging(self):
        setupLogging(debug=self.debug,directory=self.logs_dir,count=self.logs_count,
                                                        max_size=self.logs_size)
    
    def _init_signals(self):
        signal.signal(signal.SIGTERM, self._SIGTERM) 
        signal.signal(signal.SIGINT,  self._SIGINT)      
        signal.signal(signal.SIGUSR2, self._SIGUSR2)   
        signal.signal(signal.SIGHUP,  self._SIGHUP) 
        
    def init_daemon(self):
        pass

    def _SIGTERM(self,sig=None,frame=None):
        pass
        
    def _SIGINT(self,sig=None,frame=None):
        pass
        
    def _SIGUSR2(self,sig=None,frame=None):
        pass
        
    def _SIGHUP(self,sig=None,frame=None):
        pass

    def _run_children(self):
        self.sockets = [(t,create_socket(t.split(':'),self.backlog),self.backlog) for t in self.sockets.split(',')]
        logging.debug("Starting server at %s " %
                    time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        for i in xrange(self.processes):
            forked = os.fork()
            if forked == 0:
                setupLogging(i,debug=self.debug,directory=self.logs_dir,
                                count=self.logs_count,max_size=self.logs_size)
                self.runChild(i,sockets=self.sockets)
                return
            else:
                file(self.pidsdir+'/gfchild_'+str(forked)+'.pid','w+').write("%s\n" % forked)
                self.children.append(forked)         
                logging.debug("Created child # %s" % forked)
    
    def _monitor(self):
        while not self.stop_signal:
            try:
                proc = os.waitpid(-1, 0)
            except OSError,err:
                if err.errno == 4:
                    continue
            
            if self.stop_signal:
                break
                    
            if os.path.exists(self.pidsdir+'/gfchild_'+str(proc[0])+'.pid'):
                os.remove(self.pidsdir+'/gfchild_'+str(proc[0])+'.pid')
                
            logging.debug("Child # %s died" % proc[0])
            
            index = self.children.index(proc[0])
            forked = gevent.fork()
            
            if forked == 0:
                setupLogging(index,debug=self.debug,directory=self.logs_dir,
                                count=self.logs_count,max_size=self.logs_size)
                self.runChild(index,sockets=self.sockets)
                return
            else:
                file(self.pidsdir+'/gfchild_'+str(forked)+'.pid','w+').write("%s\n" % forked)
                self.children[index] = forked
                logging.debug("Created child # %s" % forked)    
     
    def start(self):
        # Check for a pidfile to see if the daemon already runs
        
        if os.path.exists(self.pidsdir+'/gfdaemon.pid'):
            message = "pidfile %s already exist. Daemon already \
    running?\n"
            print message % (self.pidsdir+'/gfdaemon.pid')
            sys.exit(0)
        
        self._daemonize()
        self._init_logging()
        self._init_signals()
        self.init_daemon()
        self._run_children()
        # Run children running monitor
        self._monitor()
    
    def stop(self):
        if self.chdir:        
            os.chdir(self.chdir)

        # Get the pid from the pidfile
        try:
            pf = file(self.pidsdir+'/gfdaemon.pid','r')
            pid = pf.read().strip()
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not \
    running?\n"
            print message % (self.pidsdir+'/gfdaemon.pid')
            sys.exit(0)

        # Try killing the daemon process       
        if int(pid) != os.getpid():
            try:
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(0.1)
            except OSError, err:	        
	
                err = str(err)

                if err.find("No such process") > 0:
                    if os.path.exists(self.pidsdir+'/gfdaemon.pid'):
                        os.remove(self.pidsdir+'/gfdaemon.pid')
                else:
                    print str(err) 
                    sys.exit(0)
                    
            # Wait for daemon proccesses to end
            while True:
                if not os.path.exists('/proc/%s' % pid):    
                    if os.path.exists(self.pidsdir+'/gfdaemon.pid'):
                        os.remove(self.pidsdir+'/gfdaemon.pid')
                    break
                time.sleep(0.3)
                    
        else:	   
            self.stop_signal = True
            
            for p in self.children:
                try:
                    os.kill(p,signal.SIGTERM)
                    if os.path.exists(self.pidsdir+'/gfchild_'+str(p)+'.pid'):
                        os.remove(self.pidsdir+'/gfchild_'+str(p)+'.pid')
                except OSError, err:	
                    pass                    
                    
            logging.debug("Server stopped at %s " %
                time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
                
            if os.path.exists(self.pidsdir+'/gfdaemon.pid'):
                os.remove(self.pidsdir+'/gfdaemon.pid')
            logging.shutdown()
            sys.exit(1)

    def reload_config(self):
        self.reload_child_configs()

    def reload_child_configs(self):

        if self.chdir:        
            os.chdir(self.chdir)

        # Get the pid from the pidfile
        try:
            pf = file(self.pidsdir+'/gfdaemon.pid','r')
            pid = pf.read().strip()
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not \
    running?\n"
            print message % (self.pidsdir+'/gfdaemon.pid')
            sys.exit(0)

        # Try killing the daemon process       
        if int(pid) != os.getpid():
            try:
                os.kill(int(pid), signal.SIGHUP)
                time.sleep(0.1)
            except OSError, err:	        
                print 'Reload signal error: ' + str(err)
        else:	         
            for i in self.children:
                try:
                    os.kill(i,signal.SIGHUP)
                    time.sleep(0.1)
                except OSError, err:	
                    print 'Reload signal error: ' + str(err)

    def restart(self):
        self.stop()
        time.sleep(0.5)
        self.start()

    def debug(self):
        if self.chdir:        
            os.chdir(self.chdir)
        self._init_signals()
        self.init_daemon()
        self.runChild(0,sockets=self.sockets)
                              
    def runChild(self,pnum,*args,**kwargs):
        """
        You should override this method when you subclass Daemon. It
        will be called after the process has been daemonized by start()
        or restart().
        """   
        
class Server(Daemon):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Server,cls).__new__(cls)
        else:
            return None
        return cls._instance

    @classmethod        
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self, app, options=None):
        socket.SOMAXCONN = get_somaxconn()
        sys.path.append(os.path.abspath(sys.argv[0]))
            
        self.options        = app.options
        self._app           = app   
        logging.debug(app.conf)
        super(Server,self).__init__(self.options)
    
    def _SIGTERM(self,sig=None,frame=None):
        self._app._stop_daemon()
        self.stop()
        
    def _SIGINT(self,sig=None,frame=None):
        self._app._stop_daemon()
        self.stop()
        
    def _SIGUSR2(self,sig=None,frame=None):
        self._app._reload_daemon_config()
        self.reload_child_configs()
        
    def _SIGHUP(self,sig=None,frame=None):
        self._app._reload_daemon_config()
        self.reload_child_configs()

    def init_daemon(self):
        set_proc_name('%sd' % self._app.name.lower())

    def runChild(self,pnum,*args,**kwargs):
        """This method runs after daemon has daemonized process as a child"""
        gevent.signal(signal.SIGTERM, self._app._stop_child) 
        gevent.signal(signal.SIGINT, self._app._stop_child)  
        gevent.signal(signal.SIGUSR2, self._app._reload_child_config)   
        gevent.signal(signal.SIGHUP, self._app._reload_child_config)   
        
        set_proc_name('%s-ch' % self._app.name.lower())
        self._app._run_child(pnum,*args,**kwargs)


    
