import pymongo
import gevent
from gevent.queue import PriorityQueue
from lib.logger import error,debug
from lib.config import Config
from lib.events import Events
import sys
import logging
import os
import time

class MongoPoolCantConnect(Exception):
    pass

class GPool(object):
    """
        Rewrited non-thread local implementation of pymongo.connection._Pool
    """

    __slots__ = ["sockets", "socket_factory", "pool_size","sock"]

    def __init__(self, socket_factory):
        object.__init__(self)
        self.pool_size = 1
        if not hasattr(self,"sock"):
            self.sock = None
        self.socket_factory = socket_factory
        if not hasattr(self, "sockets"):
            self.sockets = []

    def socket(self):
        # we store the pid here to avoid issues with fork /
        # multiprocessing - see
        # test.test_connection:TestConnection.test_fork for an example
        # of what could go wrong otherwise
        pid = os.getpid()
        if self.sock is not None and self.sock[0] == pid:
            return self.sock[1]

        try:
            self.sock = (pid, self.sockets.pop())
        except IndexError:
            self.sock = (pid, self.socket_factory())

        return self.sock[1]

    def return_socket(self):
        
        if self.sock is not None and self.sock[0] == os.getpid():
            # There's a race condition here, but we deliberately
            # ignore it.  It means that if the pool_size is 10 we
            # might actually keep slightly more than that.
            if len(self.sockets) < self.pool_size:
                self.sockets.append(self.sock[1])
            else:
                self.sock[1].close()
        self.sock = None

pymongo.connection._Pool = GPool


class MongoConnection(object):
    """Memcache pool auto-destruct connection"""
    def __init__(self,pool,conn):
        self.pool = pool
        self.conn = conn
        
    def getDB(self):
        return self.conn

    def __getattr__(self, name):
        return getattr(self.conn, name)
    
    def __getitem__(self, name):
        return self.conn[name]
                                             
    def __del__(self):
        #self.conn.connection.end_request()
        self.pool.queue.put((time.time(),self.conn))
        del self.pool
        del self.conn


class Mongo(object):    
    """MongoDB Pool"""
    def __new__(cls,size=5,*args,**kwargs):
        if not hasattr(cls,'_instance'):
            c = Config()
            cls._instance = object.__new__(cls)
            cls._instance.queue = PriorityQueue(size)
            for x in xrange(size):
                try:
                    cls._instance.queue.put(
                        (time.time(),pymongo.Connection(*args,**kwargs)[c.get('db.name','seotools')])
                    )
                except Exception,e:
                    raise MongoPoolCantConnect('Can\'t connect to mongo servers: %s' % e)
                    
        return cls._instance     
        
    def get_conn(self,block=True,timeout=None):
        """Get Mongo connection wrapped in MongoConnection"""
        obj = MongoConnection
        return obj(self,self.queue.get(block,timeout)[1]) 
        
def autoreconnect(func,*args,**kwargs):
    c = Config()
    for i in xrange(c.get('db.query_tries',20)):
        try:
            result = func(*args,**kwargs)
        except pymongo.errors.AutoReconnect:
            sys.exc_clear()
            gevent.sleep(1)
        else: 
            return result
            break

    raise MongoPoolCantConnect('Can\'t connect to DB, it may gone.')      
    
        
