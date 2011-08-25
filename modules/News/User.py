from gflib.parsing import json_encode

class UserController(object):

    def __init__(self,env,response,request,headers):
        self.env      = env
        self.headers  = headers
        self.response = response
        self.request  = request
        
    def IndexAction(self):
        self.response('200 OK', self.headers )
        return [json_encode(self.request)]
