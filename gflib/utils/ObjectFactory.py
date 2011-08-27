from weakref import WeakKeyDictionary

class ObjectFactory(object):
    
    _initialized = WeakKeyDictionary()
    
    @classmethod
    def singleton(cls,init_class,*args,**kwargs):
            if not cls._initialized.has_key(init_class):
                cls._initialized[init_class] = init_class(*args,**kwargs)
            return cls._initialized[init_class]
    
    @classmethod
    def new(cls,init_class,*args,**kwargs):
        return init_class(*args,**kwargs)

