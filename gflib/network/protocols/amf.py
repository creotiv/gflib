from gflib.network.protocols.base import BaseProtocol
from gflib.tools import wrap
from gflib.escape import utf8
from gflib.request import RequestLocalStorage
from gflib.config import Config

from pyamf.remoting.gateway.wsgi import WSGIGateway
import pyamf.remoting.gateway

import logging

c = Config()
pyamf.remoting.gateway.SERVER_NAME = c.get('server.server_name','GS')

class AMFProtocol(BaseProtocol):    
    """
        Flash AMF Protocol
    
    """
    def init(self,*args,**kvargs):
        self.gw = WSGIGateway({'CallMethod':self.run})
        
    def handler(self,env,response,request_data={}):
        #rls = RequestLocalStorage.getInstance()
        #rls.set('r',request_data)
        self.gw = WSGIGateway({'CallMethod':wrap(self.run,request_data=request_data)})
        return self.gw(env,response)

    def run(self,m,c,a,data,request_data={}):
        
        #rls = RequestLocalStorage.getInstance()
        #request_data                  = rls.get('r',{})
        request_data['r.data']        = data
        request_data['r.m']           = m
        request_data['r.c']           = c
        request_data['r.a']           = a
        
        #rls = RequestLocalStorage.getInstance()
        #rls.set('request.data',data)
        #rls.set('request.m',m)
        #rls.set('request.c',c)
        #rls.set('request.a',a)
        
        return self.base_handler(AMFRequest(request_data))
        
        
class AMFRequest(object):
            
    def __init__(self,request_data):
        self.request    = request_data
        self.status     = '200 OK'
        self.headers    = {"Server":"GS"}
            
    def write(self,data,status=' '):
        if status[0] == '5' or status[0] == '4':
            return 'Error'
        return data
            
    def debug(self,data):
        if self.conf.get('server.debug',False):
            logging.debug(data)
