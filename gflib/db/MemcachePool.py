import memcache
from gevent.queue import Queue
import sys
import logging

class MemcachedConnection(object):
    """Memcache pool auto-destruct connection"""
    def __init__(self,pool,conn):
        self.pool = pool
        self.conn = conn

    def __getattr__(self, name):
        return getattr(self.conn, name)
                           
    def __del__(self):
        self.pool.queue.put(self.conn)
        del self.pool
        del self.conn

class tempMemc(object):
    def __init__(self,p,c):
        self.pool = p
        self.conn = c
    
	def __getattr__(self, name):
		return None
    
    def set(self,*a,**k):
        return True

    def get(self,*a,**k):
        return None
        
    def __del__(self):
        self.pool.queue.put(self.conn)
        del self.pool
        del self.conn

class MemcachePool(object):    
    """Memcache Pool"""
    def __new__(cls,servers=[],size=5,temp=False):
        if not hasattr(cls,'_instance'):
            cls._instance       = object.__new__(cls)
            cls._instance.queue = Queue(size)
            cls._instance.temp  = temp
            c = Config()
            if not temp:
                for x in xrange(size):
                    try:
                        cl = memcache.Client(servers,debug=0)
                        cls._instance.queue.put(cl)
                    except:
                        sys.exc_clear()
                        logging.error('Can\'t connect to memcache servers')
            else:
                logging.debug('!!!Using dummy memcache')
                for x in xrange(size):
                    cls._instance.queue.put(None)
                    
        return cls._instance     
        
    def get_conn(self):
        """Get memcache connection wrapped in MemcachedConnection"""
        obj = MemcachedConnection
        if not self.temp:
            obj = tempMemc
        return obj(self,self.queue.get())    
