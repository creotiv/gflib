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
###################################### 

if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

class Daemon(object):

    def __init__(self,pidsdir="",processes=1,chdir=None,gid=None,uid=None):
        self.pidsdir        = pidsdir.rstrip('/ ')
        self.chdir          = chdir
        self.uid            = uid
        self.gid            = gid
        self.children       = []
        self.stop_signal    = False
        self.processes      = processes
        self.pid            = 0
        self._init_logging()
       
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

        for i in range(3):
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
        setupLogging()
    
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
        logging.debug("Starting server at %s " %
                    time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        for i in xrange(self.processes):
            forked = gevent.fork()
            if forked == 0:
                #logging.shutdown()
                setupLogging(i)
                self.runChild(i)
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
                #logging.shutdown()
                setupLogging(index)
                self.runChild(index)
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
                    time.sleep(0.1)
                except OSError, err:	
                    pass                    
            # Wait for children proccesses to end
            while True:
                exited = 0  
                for i in self.children:
                    if not os.path.exists(self.pidsdir+'gfchild_'+str(i)+'.pid'):    
                        exited += 1
                if exited == len(self.children):
                    break
                time.sleep(0.3)
                    
            logging.debug("Server stopped at %s " %
                time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
                
            if os.path.exists(self.pidsdir+'/gfdaemon.pid'):
                os.remove(self.pidsdir+'/gfdaemon.pid')
            logging.shutdown()
            sys.exit(1)

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
        self.runChild(0)
                              
    def runChild(self,pnum):
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

    def __init__(self, app, proc_num=1, chdir=None, gid=None, uid=None):
        socket.SOMAXCONN = get_somaxconn()
        self._app = app   
        sys.path.append(os.path.abspath(sys.argv[0]))
        stdout = app.logging['log']+'.log'
        stderr = app.logging['error']+'.log'
        uid = app.conf.get('server.uid',None) or uid
        gid = app.conf.get('server.gid',None) or gid
        chdir = app.conf.get('server.chdir',None) or chdir
        proc_num = app.conf.get('server.proc_num',None) or proc_num
        pidsdir = app.pidsdir
        super(Server,self).__init__(pidsdir=pidsdir,processes=proc_num,
            chdir=chdir,gid=gid,uid=uid
        )
    
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
        super(Server,self).init_daemon()

    def runChild(self, pnum):
        """This method runs after daemon has daemonized process as a child"""
        gevent.signal(signal.SIGTERM, self._app._stop_child) 
        gevent.signal(signal.SIGINT, self._app._stop_child)  
        gevent.signal(signal.SIGUSR2, self._app._reload_child_config)   
        gevent.signal(signal.SIGHUP, self._app._reload_child_config)   
        
        set_proc_name('%s-ch' % self._app.name.lower())
        self._app._run_child(pnum)

