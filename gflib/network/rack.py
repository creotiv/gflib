from gevent.event import Event

class ServerRack(object):

    def __init__(self, servers):
        self.servers = servers
        self.ev = Event()

    def start(self):
        started = []
        try:
            for server in self.servers[:]:
                server.start()
                started.append(server)
                name = getattr(server, 'name', None) or server.__class__.__name__ or 'Server'
        except:
            self.stop(started)
            raise
        
    def serve_forever(self):
        self.start()
        self.ev.wait() 

    def stop(self, servers=None):
        if servers is None:
            servers = self.servers[:]
        for server in servers:
            try:
                server.stop()
            except:
                if hasattr(server, 'loop'): #gevent >= 1.0
                    server.loop.handle_error(server.stop, *sys.exc_info())
                else: # gevent <= 0.13
                    import traceback
                    traceback.print_exc()
        self.ev.set()

