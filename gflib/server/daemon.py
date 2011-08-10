#!/usr/bin/env python

import sys
import os
import os.path
import time
import signal
import logging
import socket
import gevent
from optparse import OptionParser

# internal ########################### 
from gflib.utils import set_proc_name, get_somaxconn
###################################### 

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile="tor.pid", stdin='/dev/null',
                 stdout='/dev/null', stderr='/dev/null', processes=1, umask=0,
                 chdir=None, gid=None, uid=None):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.umask = umask
        self.chdir = chdir
        self.uid = uid
        self.gid = gid
        self.children = []
        self.stop_signal = False
        self.processes = processes
       
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = gevent.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno,\
                    e.strerror))
            sys.exit(1)

        # decouple from parent environment
        if self.chdir:        
            os.chdir(self.chdir)
        os.setsid()
        os.umask(self.umask)
        if self.uid:
            os.setuid(self.uid)
        if self.gid:
            os.setgid(self.gid)

        # do second fork
        try:
            pid = gevent.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno,\
                    e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
        pid_path = ''
        if '/' in self.pidfile:
            pid_path = os.path.join(*self.pidfile.split('/')[0:-1])+"/"
        # Run daemon process logic
        self._init_daemon()
        sys.stdout.write("\n--------------- Starting server at %s -----\
----------\n" % time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        if self.processes > 1:
            for i in xrange(self.processes):
                forked = gevent.fork()
                if forked == 0:
                    self.runChild(i)
                    return
                else:
                    file(pid_path+'chpid_'+str(forked)+'.pid','w+').write("%s\n" % forked)
                    self.children.append(forked)         
                    sys.stdout.write("Created child # %s\n" % forked)
        else:
            forked = gevent.fork()
            if forked == 0:
                self.runChild(0)
                return
            else:           
                file(pid_path+'chpid_'+str(forked)+'.pid','w+').write("%s\n" % forked)
                self.children.append(forked)
                sys.stdout.write("Created child # %s\n" % forked)
        gevent.spawn(self.runDaemon)
        # Run children running monitor
        self._monitor()
        

    def _monitor(self):
        pid_path = ''
        if '/' in self.pidfile:
            pid_path = os.path.join(*self.pidfile.split('/')[0:-1])+"/"
        while not self.stop_signal:
            try:
                proc = os.waitpid(-1, 0)
            except OSError,err:
                if err.errno == 4:
                    continue
            if os.path.exists(pid_path+'chpid_'+str(proc[0])+'.pid'):
                os.remove(pid_path+'chpid_'+str(proc[0])+'.pid')
            sys.stdout.write("Child # %s died\n" % proc[0])
            index = self.children.index(proc[0])
            forked = gevent.fork()
            if forked == 0:
                self.runChild(index)
                return
            else:
                file(pid_path+'chpid_'+str(forked)+'.pid','w+').write("%s\n" % forked)
                self.children[index] = forked
                sys.stdout.write("Created child # %s\n" % forked)                      
        
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already \
    running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
       
        # Start the daemon
        self.daemonize()

    def debug(self):
        self.runChild(0)

    def stop(self):
        """
        Stop the daemon
        """
        if self.chdir:        
            os.chdir(self.chdir)

        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not \
    running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process       
        if pid != os.getpid():
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
            except OSError, err:	        
	
                err = str(err)

                if err.find("No such process") > 0:
                    if os.path.exists(self.pidfile):
                        os.remove(self.pidfile)
                else:
                    print str(err) 
                    sys.exit(1)
                    
            # Wait for daemon proccesses to end
            while True:
                if not os.path.exists(self.pidfile):    
                    break
                time.sleep(0.3)
                    
        else:	         
            self.stop_signal = True
            for i in self.children:
                try:
                    os.kill(i,signal.SIGTERM)
                    time.sleep(0.1)
                except OSError, err:	
                    pass
                    
            pid_path = ''
            if '/' in self.pidfile:
                pid_path = os.path.join(*self.pidfile.split('/')[0:-1])+"/"
            # Wait for children proccesses to end
            while True:
                exited = 0  
                for i in self.children:
                    if not os.path.exists(pid_path+'chpid_'+str(i)+'.pid'):    
                        exited += 1
                if exited == len(self.children):
                    break
                time.sleep(0.3)
                    
            sys.stdout.write("--------------- Server stopped at %s -----\
----------\n" % time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
            logging.shutdown()
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            sys.exit(1)
            
    def reload_child_configs(self):
        """
        Reload configuration file
        """
        if self.chdir:        
            os.chdir(self.chdir)

        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not \
    running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process       
        if pid != os.getpid():
            try:
                os.kill(pid, signal.SIGUSR1)
                time.sleep(0.1)
            except OSError, err:	        
                sys.stderr.write('Reload signal error: ' + str(err))
        else:	         
            for i in self.children:
                try:
                    os.kill(i,signal.SIGUSR1)
                    time.sleep(0.1)
                except OSError, err:	
                    sys.stderr.write('Reload signal error: ' + str(err))

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        time.sleep(0.5)
        self.start()

    def _init_daemon(self):
        """Needed to initialize daemon signals, because they must be initialized
           in the main thread.
        """
        pass

    def runDaemon(self):
        """
        You should override this method when you subclass Daemon. It
        will be called after the daemon has been daemonized by start()
        or restart().
        """
    def runChild(self):
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

    def __init__(self, app, proc_num=1, umask=0, chdir=None, gid=None, uid=None):
        socket.SOMAXCONN = get_somaxconn()
        self._app = app   
        sys.path.append(os.path.abspath(sys.argv[0]))
        stdout = app.logging['log']+'.log'
        stderr = app.logging['error']+'.log'
        umask = app.conf.get('server.umask',None) or umask
        uid = app.conf.get('server.uid',None) or uid
        gid = app.conf.get('server.gid',None) or gid
        chdir = app.conf.get('server.chdir',None) or chdir
        proc_num = app.conf.get('server.proc_num',None) or proc_num
        pidfile = app.pidfile
        super(Server,self).__init__(pidfile=pidfile,processes=proc_num,
            stdout=stdout,stderr=stderr,umask=umask,chdir=chdir,gid=gid,uid=uid)

    def _init_daemon(self, *args, **kwargs):
        signal.signal(signal.SIGTERM, self._app._stop_daemon) 
        signal.signal(signal.SIGINT, self._app._stop_daemon)      
        signal.signal(signal.SIGUSR1, self._app._reload_daemon_config)   
        
        set_proc_name('%sd' % self._app.name.lower())

    def runDaemon(self, *args, **kwargs):
        """This method runs after daemon has daemonized himself and processes"""
        self._app._run_daemon(*args, **kwargs)

    def runChild(self, pnum, *args, **kwargs):
        """This method runs after daemon has daemonized process as a child"""
        gevent.signal(signal.SIGTERM, self._app._stop_child) 
        gevent.signal(signal.SIGINT, self._app._stop_child)  
        gevent.signal(signal.SIGUSR1, self._app._reload_child_config)   
        
        set_proc_name('%s-ch' % self._app.name.lower())

        self._app.run_child(pnum, *args, **kwargs)

