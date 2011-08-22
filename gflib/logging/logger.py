import logging
import logging.handlers 
import sys
# internal ###########################
from gflib.utils.config import Config    
from gflib.parsing import utf8
######################################

class NewLogger(object):
    
    @classmethod
    def error(cls,msg,*args,**kwargs):
        logging.getLogger().error(msg,*args,**kwargs)
    
    @classmethod
    def exception(cls,msg,*args,**kwargs):
        logging.getLogger().exception(msg,*args,**kwargs)
        
    @classmethod
    def log(cls,msg,*args,**kwargs):
        logging.getLogger().log(msg,*args,**kwargs)
        
    @classmethod
    def debug(cls,msg,*args,**kwargs):
        logging.getLogger().debug(msg,*args,**kwargs)
    
    
    
def setupLogging(proc="daemon"):
    """This function setup logging option for server"""
    # getting the config
    conf = Config()
    # create logger
    logger = logging.getLogger()
    
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s\
%(message)s')

    # create file handler which logs even debug messages
    if conf.get('server.debug') or proc=='daemon':
        debug = logging.handlers.RotatingFileHandler(\
            filename=conf.get("logging.debug",'gs-debug')+'-'+str(proc)+'.log',\
            mode="a",maxBytes=conf.get("logging.max_bytes",10097152),\
            backupCount=conf.get("logging.max_files",10))

        debug.setLevel(0)
        debug.setFormatter(formatter) 
        logger.addHandler(debug)        

    # create console handler with a higher log level
    error = logging.handlers.RotatingFileHandler(\
        filename=conf.get("logging.error",'gs-error')+'-'+str(proc)+'.log',\
        mode="a",maxBytes=conf.get("logging.max_bytes",10097152),\
        backupCount=conf.get("logging.max_files",10))
    error.setLevel(logging.ERROR)
    error.setFormatter(formatter)
    
    # buffer debug messages so they can be sent with error emails
    error_cache = logging.handlers.MemoryHandler(conf.get("logging.max_cache",10097152), logging.ERROR, error)
    error_cache.setLevel(logging.ERROR)    

    # add the handlers to the logger
    if conf.get('server.debug'):
        logger.addHandler(error)
    else:
        logger.addHandler(error_cache)
    
    # TODO: not working properly
    # monkey patch logging methods   
    logging.log         = logging_debug
    logging.debug       = logging_debug
    logging.error       = logging_error
    logging.exception   = logging_exception
  
  
def logging_debug(msg, *args, **kwargs):

    record = ' '.join([str(msg)]+map(str, args))

    conf = Config()

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno


    check = 'server' in conf

    if (check and conf['server']['debug']) or True:
        logger = logging
        logging.basicConfig(level=logging.DEBUG)
        format = conf.get('logging.format','%(asctime)s %(name)-12s \
%(levelname)-8s%(message)s')
        formatter = logging.Formatter(format)

        mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
        NewLogger.debug(utf8(unicode(mess)))
        
 
def logging_error(msg, *args, **kwargs):

    record = ' '.join([str(msg)]+map(str, args))

    conf = Config()

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno


    if not 'server' in conf:
        logger = logging
        logging.basicConfig(level=logging.DEBUG)
        format = conf.get('logging.format','%(asctime)s %(name)-12s \
%(levelname)-8s%(message)s')
        formatter = logging.Formatter(format)
    else:
        logger = logging.getLogger(conf['AppName'])


    mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
    NewLogger.error(utf8(unicode(mess)))
 
def logging_exception(msg, *args, **kwargs):
    
    record = ' '.join([str(msg)]+map(str, args))

    conf = Config()

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno
    
    if not 'server' in conf:
        logger = logging
        logging.basicConfig(level=logging.DEBUG)
        format = conf.get('logging.format','%(asctime)s %(name)-12s \
%(levelname)-8s%(message)s')
        formatter = logging.Formatter(format)
    else:
        logger = logging.getLogger(conf['AppName'])

    mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
    NewLogger.exception(utf8(unicode(mess)))



