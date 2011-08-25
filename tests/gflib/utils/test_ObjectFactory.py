import gc
from gflib.utils.ObjectFactory import ObjectFactory

class A(object):
    pass

class TestObjectFactory:

    def test_singleton_objects_permanents(self):
            
        a1 = ObjectFactory(A,True)  
        
        gc.collect()
        gc.collect()
        
        a2 = ObjectFactory(A,True) 
        
        assert a1 == a2, 'Singleton object return two different instances.'
        
    def test_objects_creation(self):
            
        a1 = ObjectFactory(A)  
        
        gc.collect()
        gc.collect()
        
        a2 = ObjectFactory(A) 
        
        assert a1 != a2, 'Two different instances are the same.'
        
