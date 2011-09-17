import yaml
import sys

class Config(dict):
    
    _instance = None 

    def __new__(cls,*args):
        if cls._instance is None:
            cls._instance = dict.__new__(cls)
        return cls._instance
    
    @classmethod
    def getInstance(cls):
        if not hasattr(cls,'_instance'):
            cls._instance = dict.__new__(cls)
        return cls._instance

    def reinit(self,data):
        if not isinstance(data,dict):
            raise Exception('Reinit data must be a dictionary.')
        self.update(data)

    def get(self,name,default=None):
        """Multilevel get function."""
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


