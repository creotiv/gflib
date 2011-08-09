from gflib.request import LocalStorage
from gflib.parsing import utf8

class BaseProtocol(object):
    """Base Protocol Interface"""
    def __init__(self,handler,*args,**kvargs):
        self.base_handler = handler
        self.init(*args,**kvargs)
        
    def __call__(self,env, response):
        """Executed on new request"""
        client_ip    = utf8(env.get('REMOTE_ADDR'))
        method       = utf8(env.get('REQUEST_METHOD','GET'))

        request_data                  = {}
        request_data['r.env']         = env
        request_data['r.client_ip']   = client_ip
        request_data['r.method']      = method

        # Initialize request local data
        #rls = LocalStorage.getInstance()
        #rls.set('env',env)
        #rls.set('start_response',response)        
        #rls.set('request.client_ip',client_ip)
        #rls.set('request.method',method)

        return self.handler(env, response, request_data)
                
    def init(self,*args,**kvargs):
        pass
                
    def handler(self,env,response,request_data={}):
        """API method for call request"""
        pass
