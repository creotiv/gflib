from weakref import WeakKeyDictionary

class ObjectFactory(object):
    
    _initialized = WeakKeyDictionary()
    
    def __new__(cls,init_class,single=False):
    
        if single:
            if not cls._initialized.has_key(init_class):
                cls._initialized[init_class] = init_class()
            return cls._initialized[init_class]
        else:
            return init_class()

