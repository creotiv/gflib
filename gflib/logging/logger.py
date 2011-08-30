import logging
import logging.handlers 
import sys
import os
# internal ###########################
from gflib.utils.config import Config    
from gflib.utils import utf8
######################################

class NewLogger(object):
    
    isdebug    = False
    
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
    
    
    
def setupLogging(proc="daemon",debug=False,directory='logs/',count=10,
                                                        max_size=10097152):
    """This function setup logging option for server"""
    directory = directory.rstrip(' /')
    try: 
        os.mkdir(directory)
    except OSError:
        pass
    # create logger
    logger = logging.getLogger()
    
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s\
%(message)s')

    # create file handler which logs even debug messages
    if debug or proc=='daemon':
        NewLogger.isdebug = True
        debug = logging.handlers.RotatingFileHandler(\
            filename=directory+'/gs-'+str(proc)+'-debug.log',\
            mode="a",maxBytes=max_size,backupCount=count)

        debug.setLevel(0)
        debug.setFormatter(formatter) 
        logger.addHandler(debug)        

    # create console handler with a higher log level
    error = logging.handlers.RotatingFileHandler(\
        filename=directory+'/gs-'+str(proc)+'-error.log',\
        mode="a",maxBytes=max_size,backupCount=count)
    error.setLevel(logging.ERROR)
    error.setFormatter(formatter)
    
    # buffer debug messages so they can be sent with error emails
    error_cache = logging.handlers.MemoryHandler(max_size, logging.ERROR, error)
    error_cache.setLevel(logging.ERROR)    

    # add the handlers to the logger
    if debug:
        logger.addHandler(error)
    else:
        logger.addHandler(error_cache)
    
    logging.log         = logging_debug
    logging.debug       = logging_debug
    logging.error       = logging_error
    logging.exception   = logging_exception
  
  
def logging_debug(msg, *args, **kwargs):

    if not NewLogger.isdebug:
        return

    record = ' '.join([str(msg)]+map(str, args))

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno
    
    mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
    NewLogger.debug(utf8(unicode(mess)))
        
 
def logging_error(msg, *args, **kwargs):

    record = ' '.join([str(msg)]+map(str, args))

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno

    mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
    NewLogger.error(utf8(unicode(mess)))
    
 
def logging_exception(msg, *args, **kwargs):
    
    record = ' '.join([str(msg)]+map(str, args))

    caller_file_name = sys._getframe().f_back.f_code.co_filename
    caller_file_line = sys._getframe().f_back.f_lineno
    
    mess = ''.join([' %s:%s\t\t' % (caller_file_name,caller_file_line),record])
    NewLogger.exception(utf8(unicode(mess)))



