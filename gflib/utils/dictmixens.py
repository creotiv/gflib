class MultilevelMethods(object):
    """
        Multilevel methods.
        
        Code:        
        inst.get('opt.opt_level2.key','default_value')
        inst.set('opt.opt_level2.key','value')
        inst.delete('opt.opt_level2.key')
    """
    
    __slots__ = [_dict_data,modified]    
    
    def get(self,name,default=None):
        if hasattr(self, '__dict__'):
            data = self.__dict__            
        else:
            data = self._dict_data   
        
        if not name: 
            return default
        levels = name.split('.')
        for level in levels:
            try:            
                data = data[level]
            except:
                return default

        return data

    def set(self,name,value):
        if hasattr(self, '__dict__'):
            arr = self.__dict__            
        else:
            arr = self._dict_data  

        levels = name.split('.')
        for name in levels[:-1]:
            if not arr.has_key(name):         
                arr[name] = {}   
            arr = arr[name]
        arr[levels[-1]] = value
        
    def delete(self,name,value):
        if hasattr(self, '__dict__'):
            arr = self.__dict__            
        else:
            arr = self._dict_data  
        
        levels = name.split('.')
        for name in levels[:-1]:
            if not arr.has_key(name):         
                return True 
            arr = arr[name]
            n = levels[-1]
        del arr[n]
