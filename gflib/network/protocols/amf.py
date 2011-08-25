from pyamf.remoting.gateway.wsgi import WSGIGateway
import pyamf.remoting.gateway

from gflib.utils.loader import load_module

import logging


class AMFProtocol(object):    

    def __init__(self,router,server_name='GFS'):
        pyamf.remoting.gateway.SERVER_NAME = server_name
        self.router = router
    
    def __call__(self,env,response):
        # expose_request=True - set first parametr of every service method 
        # to be WSGI environ
        gw = WSGIGateway({'CallMethod':self.router}, expose_request=True)
        return gw(env,response)
        
class AMFDOTRouter(object):
            
    def __init__(self,path='u',params='p'):
        self.path   = path
        self.params = params
        
    def __call__(self,env,request):
        if not isinstance(request,dict):
            return '400'
            
        path        = request.get(self.path,'')
        params      = request.get(self.params,{})

        try:
            if not path:
                return 400
            
            path        = map(lambda s:s.capitalize(),path.split('.'))
            path.insert(0,'modules')
            
            try:
                controller = load_module('.'.join(path[:-1]+[path[-2]+'AMFController']))
                controller = controller(env,params)  
                if not hasattr(controller,path[-1]+'Action'):
                    raise Exception('No such action %s' % '.'.join(path[:-1]+
                        [path[-2]+'Controller',path[-1]+'Action'])
                    )
            except Exception,err:
                logging.error(err)
                return 400

            return getattr(controller,path[-1]+'Action')()
            
        except Exception,e:
            logging.exception(e)
            return 500  
            
