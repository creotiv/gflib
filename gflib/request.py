from gevent.local import local

class RequestLocalStorage(local):
    _instance = None 
    _initialized = False
    
    def __new__(cls,*args,**kvargs):
        if cls._instance is None:
            cls._instance = super(RequestLocalStorage,cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = super(RequestLocalStorage,cls).__new__(cls)
        return cls._instance
        
    def __init__(self,*args,**kw):
        if self._initialized:
            raise SystemError('__init__ called too many times')
        self._initialized = True
        self.__dict__.update(kw)
        
    def get(self,name,default=None):
        """Multilevel get function.
        Code:        
        Config().get('opt.opt_level2.key','default_value')
        """
        if not name: 
            return default
        levels = name.split('.')
        data = self.__dict__            
        for level in levels:
            try:            
                data = data[level]
            except:
                return default

        return data

    def set(self,name,value):
        """Multilevel set function"""
        levels = name.split('.')
        arr = self.__dict__        
        for name in levels[:-1]:
            if not arr.has_key(name):         
                arr[name] = {}   
            arr = arr[name]
        arr[levels[-1]] = value

if __name__ == '__main__':
    import gevent

    print 'Testing: RequestLocalStorage'

    def first():
        rls = RequestLocalStorage.getInstance()
        rls.set('number',1)
        gevent.sleep(1)
        return rls.get('number')

    def second():
        rls = RequestLocalStorage.getInstance()
        rls.set('number',2)
        gevent.sleep(3)
        return rls.get('number')
    
    rls = RequestLocalStorage.getInstance()
    rls.set('number',13)
    f = gevent.spawn(first)
    s = gevent.spawn(second)
    
    f = f.get()
    s = s.get()
    b = rls.get('number')
    
    if(f == 1 and s == 2 and b == 13): 
        print 'Result: OK'
    else:
        print 'Result: Failed'
