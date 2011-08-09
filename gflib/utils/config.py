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
        """Multilevel get function.
        Code:        
        Config().get('opt.opt_level2.key','default_value')
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
        """Multilevel set function"""
        levels = name.split('.')
        arr = self        
        for name in levels[:-1]:
            if not arr.has_key(name):         
                arr[name] = {}   
            arr = arr[name]
        arr[levels[-1]] = value


class InitConfig(object):

    def __new__(cls, path=''):
        try:
            stream = file(path, 'r')
            data = yaml.load(stream)
            stream.close()
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print "Error position: (%s:%s)" % (mark.line+1, mark.column+1)
                sys.exit()

        conf = Config(data)
        return conf
