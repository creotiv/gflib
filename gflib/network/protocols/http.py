from gflib.parsing import utf8,json_encode

from cgi import parse_multipart
from urlparse import parse_qs
from cStringIO import StringIO
import logging


class HTTPProtocol(object):    

    def __init__(self,router):
        self.router      = router
        
    def __call__(self,env,response):
        return self.router(env,response)
            

class HTTPDOTRouter(object):
            
    def __init__(self,path='u',default_headers=[('Server','GFS')]):
        self.path               = path
        self.default_headers    = default_headers
        
    def getAction(self,path):
        
        return module,controller,action
        
    def __call__(self,env,response):
        method       = utf8(env.get('REQUEST_METHOD','GET')) 
        get_string   = utf8(env.get('QUERY_STRING',''))
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
            path        = data.get(self.path,None)
            if not path:
                response('400 Bad Request', self.default_headers )
                return [json_encode({'error':400,'msg':'Bad Request.'})]
                
            params      = data
            
            response('200 OK', self.default_headers )
            return [json_encode(data)]
        except Exception,e:
            response('500 Internal Server Error', self.default_headers )
            logging.exception(e)
            return [json_encode({'error':500,'msg':'Internal Server Error'})]      
            
              
