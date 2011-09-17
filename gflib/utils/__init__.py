import functools
import gc
import inspect
import logging
import signal
import os
import re

from escape import *

def load_yaml(path):
    try:
        stream = file(path, 'r')
        data = yaml.load(stream)
        stream.close()
        return data
    except yaml.YAMLError, exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            logging.error("YAML %s Error at position: (%s:%s)" % (path,mark.line+1, mark.column+1))
            return False

def wrap(method, *args, **kargs):
    if method is None:
        return None
    if args or kargs:
        method = functools.partial(method, *args, **kargs)
    def wrapper(*args, **kargs):
        return method(*args, **kargs)
    return wrapper

def get_somaxconn():
    try:
        f = open('/proc/sys/net/core/somaxconn','r')
        res = int(f.read().strip())
        f.close()
        return res
    except:
        logging.error(' Can\'t get somaxconn constant from\
 /proc/sys/net/core/somaxconn setting to the 128')
        return 128

def set_proc_name(newname):
    """Setting process name"""
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def get_proc_name():
    """Getting process name"""
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(128)
    # 16 == PR_GET_NAME from <linux/prctl.h>
    libc.prctl(16, byref(buff), 0, 0, 0)
    return buff.value
    
def get_domain(url,subdomain=False):
    TLDS = ["AC","AD","AE","AERO","AF","AG","AI","AL","AM","AN","AO","AQ","AR",
            "ASIA","AT","AU","AW","AX","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BIZ",
            "BJ","BM","BN","BO","BR","BS","BT","BV","BW","BY","BZ","CA","CAT","CC","CD",
            "CF","CG","CH","CI","CK","CL","CM","CN","CO","COM","COOP","CR","CU","CV","CX",
            "CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EDU","EE","EG","ER","ES","ET",
            "EU","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE","GF","GG","GH","GI","GL",
            "GM","GN","GOV","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR",
            "HT","HU","ID","IE","IL","IM","IN","INFO","INT","IO","IQ","IR","IS","IT","JE",
            "JM","JO","JOBS","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ",
            "LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","ME","MG",
            "MH","MIL","MK","ML","MM","MN","MO","MOBI","MP","MQ","MR","MS","MT","MU",
            "MUSEUM","MV","MW","MX","MY","MZ","NA","NAME","NC","NE","NET","NF","NG","NI",
            "NL","NO","NP","NR","NU","NZ","OM","ORG","PA","PE","PF","PG","PH","PK","PL",
            "PM","PN","PR","PRO","PS","PT","PW","PY","QA","RE","RO","RS","RU","RW","SA",
            "SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","ST","SU",
            "SV","SY","SZ","TC","TD","TEL","TF","TG","TH","TJ","TK","TL","TM","TN","TO",
            "TP","TR","TRAVEL","TT","TV","TW","TZ","UA","UG","UK","US","UY","UZ","VA","VC",
            "VE","VG","VI","VN","VU","WF","WS","YE","YT","ZA","ZM","ZW","ARPA","AS"]

    reg_domain = re.compile("https?://(?:www\.)?([^\/\?\#]+).*$",re.I | re.U | re.S)
    domain = reg_domain.sub(r"\1",url).split('.')
    if subdomain:
        return '.'.join(domain)
    if (domain[-1].upper() in TLDS) and (domain[-2].upper() in TLDS):
        res = '.'.join(domain[-3:])
    else:
        res = '.'.join(domain[-2:])
    return res
       
def dump_garbage():
    # force collection
    logging.debug("Collecting GARBAGE: %s" % gc.collect())
    
    # prove they have been collected
    logging.debug("Collecting GARBAGE: %s" % gc.collect())
    
    logging.debug("GARBAGE OBJECTS:")
    for x in gc.garbage:
        s = str(x)
        if len(s) > 80: s = "%s..." % s[:80]
        
        logging.debug(":: %s" % s)
        logging.debug("        type: %s" % type(x))
        logging.debug("   referrers: %s" % len(gc.get_referrers(x)))
        try:
            logging.debug("    is class: %s" % inspect.isclass(type(x)))
            logging.debug("      module: %s" % inspect.getmodule(x))
            
            lines, line_num = inspect.getsourcelines(type(x))
            logging.debug("    line num: %s" % line_num)
            for l in lines:
                logging.debug("        line: %s" % l.rstrip("\n"))
        except:
            pass

        logging.debug('')
        

def yaml_to_dict(path=''):
    try:
        stream = file(path, 'r')
        data = yaml.load(stream)
        stream.close()
    except yaml.YAMLError, exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            logging.error("Config error at position: (%s:%s)" % 
                                                (mark.line+1, mark.column+1)
            )

    return data
