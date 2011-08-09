import sys
import os
import logging

def _importAndCheckStack(importName):
    """
    Import the given name as a module, then walk the stack to determine whether
    the failure was the module not existing, or some code in the module (for
    example a dependent import) failing.  This can be helpful to determine
    whether any actual application code was run.  For example, to distiguish
    administrative error (entering the wrong module name), from programmer
    error (writing buggy code in a module that fails to import).
    """
    try:
        try:
            mod = __import__(importName)
            return mod
        except:
            excType, excValue, excTraceback = sys.exc_info()
            while excTraceback:
                execName = excTraceback.tb_frame.f_globals["__name__"]
                if (execName is None or # python 2.4+, post-cleanup
                    execName == importName): # python 2.3, no cleanup
                    raise excType, excValue, excTraceback
                excTraceback = excTraceback.tb_next
            raise 
    except:
        # Necessary for cleaning up modules in 2.3.
        sys.modules.pop(importName, None)
        raise

LoadModuleError(Exception):
    pass

def load_module(name):
    """
	Load Python modules and returns it object
    """
    if not name:
        raise 

    names = name.split('.')

    # if the name starts or ends with a '.' or contains '..', the __import__
    # will raise an 'Empty module name' error. This will provide a better error
    # message.
    if '' in names:
        raise LoadModuleError('Malformed path')

    topLevelPackage = None
    moduleNames = names[:]
    while not topLevelPackage:
        if moduleNames:
            trialname = '.'.join(moduleNames)
            try:
                topLevelPackage = _importAndCheckStack(trialname)
            except Exception,err:
                moduleNames.pop()
        else:
            if len(names) == 1:
                raise 
            else:
                raise 

    obj = topLevelPackage
   
    for n in names[1:]:
        try:
            obj = getattr(obj, n)
        except Exception, err:
            raise LoadModuleError('Can\'t load module `%s`: %s' % ('.'.join(names),err))
    return obj
