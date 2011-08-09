__author__ = "Andrey Nikishaev"
__copyright__ = "Copyright 2010, http://creotiv.in.ua"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Andrey Nikishaev"
__email__ = "creotiv@gmail.com"
__status__ = "Production"

"""
Examples of use:

def in_another_greenlet():
    print '001',getcurrent()
    
def in_another_greenlet2():
    print '002',getcurrent()
 
def test_subscribe():
    e = Observer()
    print '000',getcurrent()
    getcurrent().in_another_greenlet = in_another_greenlet
    getcurrent().in_another_greenlet2 = in_another_greenlet2
    b = e.subscribe('kill',getcurrent().in_another_greenlet)
    c = e.subscribe('kill',getcurrent().in_another_greenlet2)
 
def test_wait():
    e = Observer()
    ev = e.wait('kill')
    try:
        gevent.sleep(3)
    except FiredEvent:
        print 'Fired!'
    else:
        print 'Not Fired!'
    finally:
        ev.cancel()
 
def fire_event():
    e2 = Observer()
    gevent.sleep(2)
    e2.fire('kill')
 
p = Pool()
p.spawn(test_wait)
p.spawn(test_subscribe)
p.spawn(fire_event)
 
p.join()
"""

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
        gevent.spawn(self.callback)
 
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
        

if __name__ == '__main__': 
    # Testing
    def in_another_greenlet():
        print '001',getcurrent()
        
    def in_another_greenlet2():
        print '002',getcurrent()
     
    def test_subscribe():
        e = Observer()
        print '000',getcurrent()
        getcurrent().in_another_greenlet = in_another_greenlet
        getcurrent().in_another_greenlet2 = in_another_greenlet2
        b = e.subscribe('kill',getcurrent().in_another_greenlet)
        c = e.subscribe('kill',getcurrent().in_another_greenlet2)
        gevent.sleep(5)
        print 'END'
        b.unsubscribe()
        c.unsubscribe()
     
    def test_wait():
        e = Observer()
        ev = e.wait('kill')
        try:
            gevent.sleep(3)
        except FiredEvent:
            print 'Fired!'
        else:
            print 'Not Fired!'
        finally:
            ev.cancel()

    def fire_event():
        e2 = Observer()
        gevent.sleep(2)
        e2.fire('kill')
     
    p = Pool()
    p.spawn(test_wait)
    p.spawn(test_subscribe)
    p.spawn(fire_event)
     
    p.join()

