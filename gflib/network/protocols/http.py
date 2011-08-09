from gflib.logging.firepy import FirePy
from gflib.network.protocols.base import BaseProtocol
from gflib.utils import wrap
from gflib.parsing import utf8
from gflib.utils.config import Config
from gflib.db.storage import LocalStorage

from cgi import parse_multipart
from urlparse import parse_qs
from cStringIO import StringIO
import logging
import time

class HTTPProtocol(BaseProtocol):    
    """
        HTTP Protocol
    
    """
    def handler(self,env,response,request_data={}):
        method       = utf8(env.get('REQUEST_METHOD','GET')) 
        get_string   = utf8(env.get('QUERY_STRING',''))
        client_ip    = utf8(env.get('REMOTE_ADDR'))
        content_type = utf8(env.get('CONTENT_TYPE','').lower())
        
        GET = {}
        POST = {}

        if content_type == 'multipart/form-data':
        
            ctype, pdict = cgi.parse_header(content_type)        
            if get_string:
                GET = parse_qs(
                    get_string,
                    keep_blank_values=True
                )
            if method == 'POST':
                POST = cgi.parse_multipart(env.copy()['wsgi.input'].read(), pdict)
        
        else:
        
            if get_string:
                GET = parse_qs(
                    get_string,
                    keep_blank_values=True
                )
            if method == 'POST':
                POST = parse_qs(
                    env.copy()['wsgi.input'].read(),
                    keep_blank_values=True
                )
            
        data = dict(GET)
        data.update(dict(POST))
    
        try:
            m,c,a = data.get('a','')[0].split('.')
            
            request_data['r.data']    = data
            request_data['r.m']       = m
            request_data['r.c']       = c
            request_data['r.a']       = a
            
            #rls = LocalStorage.getInstance()
            #rls.set('request.data',data)
            #rls.set('request.m',m)
            #rls.set('request.c',c)
            #rls.set('request.a',a)
            return self.base_handler(HTTPRequest(request_data,response))
        except Exception,e:
            response('404 Not Found', [])
            return [utf8(unicode(e))]


class HTTPRequest(object):
    
    def __init__(self,request_data,response,status='200 OK'):
        self.request    = request_data
        self.status     = status
        self.response   = response
        self.logs       = []
        self.logging    = FirePy()
        self.conf       = Config()
        self.headers    = {"Server":self.conf.get('server.server_name','GS')}
            
    def write(self,data,status=None):
        status = status if status else self.status
        
        headers = []
        if self.conf.get('server.debug',False):

            for h in self.headers.items():
                headers.append(h)
            for h in self.logging.base_headers():
                headers.append(h)
            for h in self.logging.generate_headers():
                headers.append(h)

        else:
            headers = self.headers.items()
        
        self.response(status,headers)
        return [data]
            
    def debug(self,data):
        if self.conf.get('server.debug',False):
            self.logging.log(data)
                
