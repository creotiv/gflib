from gflib.utils.observer import Observer,FiredEvent
import gevent
from gevent.hub import getcurrent
from gevent.pool import Pool

class TestObserver:

    def in_another_greenlet(self):
        self.a1 = getcurrent()
        
    def in_another_greenlet2(self):
        self.a2 = getcurrent()
     
    def run_subscribe(self):
        e = Observer()
        getcurrent().in_another_greenlet = self.in_another_greenlet
        getcurrent().in_another_greenlet2 = self.in_another_greenlet2
        b = e.subscribe('kill',getcurrent().in_another_greenlet)
        c = e.subscribe('kill',getcurrent().in_another_greenlet2)
        gevent.sleep(1)
        b.unsubscribe()
        c.unsubscribe()
     
    def run_wait(self):
        e = Observer()
        ev = e.wait('kill')
        try:
            gevent.sleep(1)
        except FiredEvent:
            return True
        else:
            return False
        finally:
            ev.cancel()

    def run_cancel(self):
        try:
            e = Observer()
            ev = e.wait('kill')
            ev.cancel()
            gevent.sleep(1)
        except FiredEvent:
            return False
        else:
            return True

    def fire_event(self):
        e2 = Observer()
        e2.fire('kill')
     
    def test_wait(self): 
        p = Pool()
        w = p.spawn(self.run_wait)
        f = p.spawn(self.fire_event)
        p.join()

        assert w.value, 'Event not fired in while it was waited.'
        
    def test_subscribe(self): 
        p = Pool()
        p.spawn(self.run_subscribe)
        p.spawn(self.fire_event)
        p.join()

        assert self.a1 != self.a2 and str(self.a1) and str(self.a2),\
               'Event not fired in while it was subscribed.'
               
    def test_cancel(self):
        p = Pool()
        w = p.spawn(self.run_cancel)
        f = p.spawn(self.fire_event)
        p.join()

        assert w.value, 'Event fired while it was canceled.'
               
               
