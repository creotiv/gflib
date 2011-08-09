import gevent
from gevent.coros import Semaphore

import os
import os.path
import shutil

import cPickle

class LocalDBException(Exception):
    pass

class LoadData(LocalDBException):
    pass
    
class SaveData(LocalDBException):
    pass

class LocalDB(object):
    """
        Local DB  - in memory hash db with saving to hard drive.
        
        TODO:
            - Create queue for set requests to remove locking on this operation.
    """
    def __init__(self,db_path='localdb.dat',save_interval=5):
        self.db_path        = db_path
        self.save_interval  = save_interval
        self.modified       = False
        self.data           = {}
        self.wlock          = Semaphore()
        
        gevent.spawn_later(self.save_interval*60,self.save_handler)
        
        if os.path.exists(self.db_path):
            try:
                fp = file(self.db_path,'rb')
                self.data = cPickle.load(fp)
                fp.close()
            except Exception,e:
                raise LoadData('Failed to load data to LocalDB (%s): %s' % (self.db_path,e))

    def save(self):
        self.save_handler(restart=False)

    def save_handler(self,restart=True):
        if not self.modified:
            return
        try:
            if os.path.exists(self.db_path):
                shutil.copyfile(self.db_path,self.db_path+'.tmp')
            fp = file(self.db_path,'wb')
            cPickle.dump(self.data,fp)
            fp.close()
        except Exception,e:
            try:
                shutil.copyfile(self.db_path+'.tmp',self.db_path)
            except Exception:
                pass
            raise SaveData('Failed to save data to LocalDB (%s): %s' % (self.db_path,e))       
        finally:
            try:
                os.unlink(self.db_path+'.tmp')
            except:
                pass
            if restart:
                gevent.spawn_later(self.save_interval*60,self.save_handler) 
        
    def get(self,name,default=None):
        """Multilevel get function.
        Code:        
        Config().get('opt.opt_level2.key','default_value')
        """
        if not name: 
            return default
        levels = name.split('.')
        data = self.data            
        for level in levels:
            try:            
                data = data[level]
            except:
                return default

        return data
    
    def set(self,name,value):
        """Multilevel set function
        Code:        
        Config().set('opt.opt_level2.key','default_value')
        """
        self.wlock.acquire()
        self.modified = True
        levels = name.split('.')
        arr = self.data        
        for name in levels[:-1]:
            if not arr.has_key(name):         
                arr[name] = {}   
            arr = arr[name]
        arr[levels[-1]] = value
        self.wlock.release()
        
    def delete(self,name,value):
        """Multilevel delete function
        Code:        
        Config().delete('opt.opt_level2.key','default_value')
        """
        self.wlock.acquire()
        self.modified = True
        levels = name.split('.')
        arr = self.data        
        for name in levels[:-1]:
            if not arr.has_key(name):         
                return True 
            arr = arr[name]
            n = levels[-1]
        del arr[n]
        self.wlock.release()
        
    def getset(self,name,value):
        """Get cache, if not exists set it and return set value
        Code:        
        Config().getset('opt.opt_level2.key','default_value')
        """
        g = self.get(name)
        if not g:
            g = value
            self.set(name,g)
        return g
        
        
