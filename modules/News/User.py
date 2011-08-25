from gflib.parsing import json_encode

class UserHTTPController(object):

    def __init__(self,env,response,request,headers):
        self.env      = env
        self.headers  = headers
        self.response = response
        self.request  = request
        
    def IndexAction(self):
        self.response('200 OK', self.headers )
        return [json_encode(self.request)]
        
class UserAMFController(object):

    def __init__(self,env,request):
        self.env      = env
        self.request  = request
        
    def IndexAction(self):
        return [json_encode(self.request)]
