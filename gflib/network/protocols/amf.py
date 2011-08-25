from pyamf.remoting.gateway.wsgi import WSGIGateway
import pyamf.remoting.gateway

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
            
        path        = env.get(self.path,'')
        params      = request.get(self.params,[[],{}])
        
        return [path,params]
