import sys

import gevent
from gevent import core
from gevent.hub import getcurrent
from gevent.event import Event
from gevent.pool import Pool
# internal ###########################
from gflib.utils import wrap
###################################### 
 
class FiredEvent:
    pass
 
class Event(object):
 
    __slot__ = ['events','name','callback']
 
    def __init__(self,events,name,callback):
        self.events = events
        self.name = name.lower()
        self.callback = callback
 
    def unsubscribe(self):
        if not self.events._events.has_key(self.name):
            return True
        try:
            del self.events._events[self.name][self.events._events[self.name].index(self)]
        except:
            pass
        return True
 
    def cancel(self):
        self.unsubscribe()
 
    def run(self):
        g = gevent.spawn(self.callback)
 
    def __del__(self):
        self.unsubscribe()
 
class Observer(object):
 
    def __new__(cls,*args):
        if not hasattr(cls,'_instance'):
            cls._instance = object.__new__(cls)
            cls._instance._events = {}
        return cls._instance
 
    def subscribe(self,name,callback):
        if not self._events.has_key(name.lower()):
            self._events[name] = []
        ev = Event(self,name,callback)
        self._events[name].append(ev)
        return ev
 
    def fire(self,name):
        try:
            ev = self._events[name.lower()].pop(0)
        except:
            return False
        while ev:
            gevent.spawn(ev.run)
            try:
                ev = self._events[name.lower()].pop(0)
            except:
                break
        return True
 
    def wait(self,name):
        if not self._events.has_key(name.lower()):
            self._events[name] = []
        ev = Event(self,name,wrap(getcurrent().throw,FiredEvent))
        self._events[name].append(ev)
        return ev

