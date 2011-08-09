class conf(object):
    def __init__(self, setup=None,teardown=None):
        self.setup = setup
        self.teardown = teardown

    def __call__(self, meth):
        def wrap(this,*args,**kvargs):
            if callable(self.setup):
                self.setup()
            else:
                getattr(this,self.setup,lambda:True)()
            res = meth(this,*args,**kvargs)
            if callable(self.teardown):
                self.teardown()
            else:
                getattr(this,self.teardown,lambda:True)()
            return res
        return wrap
