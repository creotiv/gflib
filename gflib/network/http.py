import gevent

import urllib2
import urllib
import cStringIO
import sys
import gzip
import random
import time
import socket
import logging

from lib.escape import json_decode

class TimeoutException(Exception):
    pass

def Get(url,post=None,cookie=None):
    
    post = urllib.urlencode(post)
    
    urllib2.HTTPRedirectHandler.max_redirections = 1
    if cookie:
        opener = urllib2.build_opener(cookie)
    else:
        opener = urllib2.build_opener()
    
    
    opener.addheaders = [
        ('User-Agent', 'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; \
         en-US; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.1 '), 
        ('Accept', 'image/png,image/*;q=0.8,*/*;q=0.5'),
        ('Accept-Language', 'en-us,en;q=0.5'),
        ('Accept-Encoding', 'gzip,deflate'),
        ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
        ('Keep-Alive', '3600'),
        ('Connection', 'keep-alive'),
        ('Host','lottery.gof')
    ]
    
    t = gevent.Timeout(15,TimeoutException)
    t.start()
    
    try:
        r = opener.open(url,data=post,timeout=15)
        headers = r.info()
        html = r.read()
    except urllib2.HTTPError,e:
        logging.debug('%s -- HTTP ERROR: (%s)' % (url+'?'+post,e))
        sys.exc_clear()
        return None
    except urllib2.URLError,e:
        logging.debug('%s -- URL ERROR: (%s)' % (url+'?'+post,e))
        sys.exc_clear()
        return None
    except TimeoutException:
        logging.debug('%s -- TIMEOUT ERROR' % (url+'?'+post))
        timeout = True
        sys.exc_clear()
        return None
    except Exception,e:
        logging.debug('%s -- ERROR: (%s)' % (url+'?'+post,e))
        sys.exc_clear()
        return None
    finally:
        t.cancel()
      
   
    
    if ('Content-Encoding' in headers.keys() and headers['Content-Encoding']=='gzip') or \
       ('content-encoding' in headers.keys() and headers['content-encoding']=='gzip'):
        data = cStringIO.StringIO(html)
        gzipper = gzip.GzipFile(fileobj=data)
        # Some servers may return gzip header, but not zip data.
        try:
            html_unzipped = gzipper.read()
        except:
            html = None
            sys.exc_clear()    
        else:
            html = html_unzipped

    try:
        return json_decode(html)
    except Exception,e:
        logging.debug('%s -- JSON PARSE ERROR: (%s) with: \n%s\n' % (url+'?'+post,e,html))
        sys.exc_clear()
        return None

