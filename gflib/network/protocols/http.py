from gflib.utils import utf8,json_encode,json_decode
from gflib.utils.loader import load_module
from gflib.network.distribution import Network

from gevent.pool import Pool
from cgi import parse_multipart
from urlparse import parse_qs
from cStringIO import StringIO
import logging


class HTTPProtocol(object):    

    def __init__(self,router):
        self.router      = router
        
    def __call__(self,env,response):
        return self.router(env,response)
            

class WSGIResponse(object):
    
    def __init__(self):
        self.status  = '200 OK'
        self.headers = []
        
    def __call__(self,status,headers):
        self.status  = status
        self.headers = headers
    
    def toDict(self):
        return {'s':self.status,'h':self.headers}
        
        
class DistributedHTTPDOTRouter(object):
            
    def __init__(self,servers,iopool,path='u',default_headers=[('Server','GFS')]):
        self.path               = path
        self.default_headers    = default_headers
        self.servers            = servers
        self.iopool             = iopool

    def __call__(self,env,response):
        try:
            dheaders = dict(self.default_headers)
            nt = Network(200,'REQ',self.servers,self.iopool)
            nt = nt.get_socket()
            try:
                inputdata = env['wsgi.input'].read()
                env['wsgi.input'] = inputdata
                env['wsgi.errors'].close()
                del env['wsgi.errors']
                nt.send({'env':env})
                res = nt.recv()
            except Exception,e:
                logging.debug('500x0 Internal Server Error')
                logging.error(e)
                
            if not isinstance(res,dict): 
                logging.debug('500x1 Internal Server Error')
                response('500 Internal Server Error', self.default_headers)
                return [json_encode({'error':500,'msg':'Internal Server Error'})]  
            if isinstance(res,dict) and res.has_key('e'):  
                logging.debug('500x2 Internal Server Error: %s' % res['e'])
                response('500 Internal Server Error', self.default_headers)
                return [json_encode({'error':res['e'],'msg':'Worker error'})]  
                
            headers = dheaders
            status  = '200 OK' 
            if isinstance(res,dict) and res.has_key('h'): 
                headers  = res['h']
                for i in xrange(len(headers)):
                    headers[i] = tuple(headers[i]) 
            if isinstance(res,dict) and res.has_key('s'): 
                status   = res['s']
            data         = res['d']
            response(status, headers)
            return [utf8(data[0])]
        except Exception,e:
            logging.exception(e)
        
    def _loop(self):
        try:
            nt = Network(300,'REP2',self.servers,self.iopool)
            nt = nt.get_socket()
            while True:
                message = nt.recv()
                res = self.process(message)
                nt.send(res)
        except Exception,e:
            logging.exception(e)
            
    def serve_forever(self):
        pool = Pool()
        for i in xrange(300):
            pool.spawn(self._loop)
        pool.join()
        
    def process(self,msg):
        if not isinstance(msg,dict) or not msg.has_key('env'):
            return {'e':400}
            
        env      = msg['env']
        response = WSGIResponse()
    
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
                POST = cgi.parse_multipart(env.copy()['wsgi.input'], pdict)
        
        else:
        
            if get_string:
                GET = parse_qs(
                    get_string,
                    keep_blank_values=True
                )
            if method == 'POST':
                POST = parse_qs(
                    env.copy()['wsgi.input'],
                    keep_blank_values=True
                )
            
        data = dict(GET)
        data.update(dict(POST))
    
        try:
            path        = data.get(self.path,'')
            if not path:
                return {'e':401}
            
            params      = data
            path        = map(lambda s:s.capitalize(),path[0].split('.'))
            path.insert(0,'modules')

            try:
                controller = load_module('.'.join(path[:-1]+[path[-2]+'HTTPController']))
                controller = controller(env,response,data,self.default_headers)  
                if not hasattr(controller,path[-1]+'Action'):
                    raise Exception('No such action %s' % '.'.join(path[:-1]+
                        [path[-2]+'Controller',path[-1]+'Action'])
                    )
            except Exception,err:
                logging.error(err)
                return {'e':402}

            res = getattr(controller,path[-1]+'Action')()
            d = response.toDict()
            d.update({'d':res})
            return d

        except Exception,e:
            logging.exception(e)
            return {'e':500}   
            

class HTTPDOTRouter(object):
            
    def __init__(self,path='u',default_headers=[('Server','GFS')]):
        self.path               = path
        self.default_headers    = default_headers
        
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
            path        = data.get(self.path,'')
            if not path:
                response('400 Bad Request', self.default_headers )
                return [json_encode({'error':400,'msg':'Bad Request.'})]
            
            params      = data
            path        = map(lambda s:s.capitalize(),path[0].split('.'))
            path.insert(0,'modules')

            try:
                controller = load_module('.'.join(path[:-1]+[path[-2]+'HTTPController']))
                controller = controller(env,response,data,self.default_headers)  
                if not hasattr(controller,path[-1]+'Action'):
                    raise Exception('No such action %s' % '.'.join(path[:-1]+
                        [path[-2]+'Controller',path[-1]+'Action'])
                    )
            except Exception,err:
                logging.error(err)
                response('400 Bad Request', self.default_headers )
                return [json_encode({'error':400,'msg':'Bad Request.'})]

            return getattr(controller,path[-1]+'Action')()

        except Exception,e:
            logging.exception(e)
            response('500 Internal Server Error', self.default_headers )
            return [json_encode({'error':500,'msg':'Internal Server Error'})]     
            

