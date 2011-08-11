from gevent.local import local

class SimpleCache(dict):
    
    def __new__(cls,*args):
        if not hasattr(cls,'_instance'):
            cls._instance = dict.__new__(cls)
        return cls._instance
    
    @classmethod
    def getInstance(cls):
        if not hasattr(cls,'_instance'):
            cls._instance = dict.__new__(cls)
        return cls._instance

    def get(self,name,default=None):
        """Multilevel get function.
        Code:        
        inst.get('opt.opt_level2.key','default_value')
        """
        if not name: 
            return default
        levels = name.split('.')
        data = self            
        for level in levels:
            try:            
                data = data[level]
            except:
                return default

        return data
    
    def set(self,name,value):
        """Multilevel set function
        Code:        
        inst.set('opt.opt_level2.key','default_value')
        """
        levels = name.split('.')
        arr = self        
        for name in levels[:-1]:
            if not arr.has_key(name):         
                arr[name] = {}   
            arr = arr[name]
        arr[levels[-1]] = value
        
    def getset(self,name,value):
        """Get cache, if not exists set it and return set value
        Code:        
        inst.getset('opt.opt_level2.key','default_value')
        """
        g = self.get(name)
        if not g:
            g = value
            self.set(name,g)
        return g

def scache(func):
    def wrapper(*args, **kwargs):
        cache = SimpleCache()
        fn = "scache." + func.__module__ + func.__class__.__name__ + \
             func.__name__ + str(args) + str(kwargs)		
        val = cache.get(fn)
        if not val:
            res = func(*args, **kwargs)
            cache.set(fn,res)
            return res
        return val
    return wrapper

class LocalStorage(local):
    _instance = None 
    _initialized = False
    
    def __new__(cls,*args,**kvargs):
        if cls._instance is None:
            cls._instance = super(LocalStorage,cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = super(LocalStorage,cls).__new__(cls)
        return cls._instance
        
    def __init__(self,*args,**kw):
        if self._initialized:
            raise SystemError('__init__ called too many times')
        self._initialized = True
        self.__dict__.update(kw)
        
    def get(self,name,default=None):
        """Multilevel get function.
        Code:        
        inst.get('opt.opt_level2.key','default_value')
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

    print 'Testing: LocalStorage'

    def first():
        rls = LocalStorage.getInstance()
        rls.set('number',1)
        gevent.sleep(1)
        return rls.get('number')

    def second():
        rls = LocalStorage.getInstance()
        rls.set('number',2)
        gevent.sleep(3)
        return rls.get('number')
    
    rls = LocalStorage.getInstance()
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
