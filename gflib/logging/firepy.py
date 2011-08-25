# The MIT License
# 
# Copyright (c) 2009 Sung-jin Hong <serialx@serialx.net>
# Many code here derived from:
# http://code.cmlenz.net/diva/browser/trunk/diva/ext/FirePy.py
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from gflib.parsing import utf8,json_encode
import logging
import sys

# Max size of eash headers. Exists because Firefox has limits (5000)
HEADER_SIZE_MAX = 4000


def _extract_traceback(tb):
    frames = []
    while tb:
        tb_frame = tb.tb_frame
        f_locals = tb_frame.f_locals
        f_code = tb_frame.f_code
        frames.append({
            'filename': f_code.co_filename,
            'lineno': tb.tb_lineno,
            'locals': f_locals,
            'name': f_code.co_name,
            'args': [
                #f_code.co_varnames[i] for i in range(f_code.co_argcount)
                f_locals.get(f_code.co_varnames[i]) for i in range(f_code.co_argcount)
            ],
            'hide': tb_frame.f_locals.get('__traceback_hide__')
        })
        tb = tb.tb_next
    return frames

def _filter_traceback(frames):
    hidden = False
    retval = []
    for idx, frame in enumerate(frames):
        hide = frame['hide']
        if hide in ('before', 'before_and_this'):
            del retval[:]
            hidden = False
            if hide == 'before_and_this':
                continue
        elif hide in ('reset', 'reset_and_this'):
            hidden = False
            if hide == 'reset_and_this':
                continue
        elif hide in ('after', 'after_and_this'):
            hidden = True
            if hide == 'after_and_this':
                continue
        elif hidden:
            continue
        if not hide:
            retval.append(frame)
    return retval


class FirePy(object):
    """Core module that generates FirePy JSON notation."""
    VERSION = '0.3'
    
    def __init__(self):
        self.logs = []

    def log(self, data):
        """Translate log record into FirePy JSON."""
        pathname = sys._getframe().f_back.f_code.co_filename
        lineno = sys._getframe().f_back.f_lineno
        
        logger = logging
        logging.basicConfig(level=logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s\
%(message)s')

        data = json_encode(data) if not isinstance(data,str) else data
        mess = ''.join([' %s:%s ' % (pathname,lineno),data])
        logger.debug(mess)

        self.logs.append([
            {"Type": 'LOG',
             "File": pathname,
             "Line": lineno},
             data]
        )

    def base_headers(self):
        """Base FirePHP JSON protocol headers."""
        return [
            ('X-Wf-Protocol-1',
             'http://meta.wildfirehq.org/Protocol/JsonStream/0.2'),
            ('X-Wf-1-Plugin-1',
             'http://meta.firephp.org/Wildfire/Plugin/FirePHP/Library-FirePHPCore/'+self.VERSION),
            ('X-Wf-1-Structure-1',
             'http://meta.firephp.org/Wildfire/Structure/FirePHP/FirebugConsole/0.1'),
            ]

    def generate_headers(self):
        def encode_robust(obj):
            return repr(obj)
        index = 1
        for log in self.logs:
            code = json_encode(log)
            if len(code) >= HEADER_SIZE_MAX:  # Too large header for firefox, split it
                cut = code[:HEADER_SIZE_MAX]
                rest = code[HEADER_SIZE_MAX:]
                logging.debug(cut)
                yield ('X-Wf-1-1-1-%d' % index, '%d|%s|\\' % (len(code), cut))
                index += 1
                while True:
                    cut = rest[:HEADER_SIZE_MAX]
                    rest = rest[HEADER_SIZE_MAX:]
                    if rest:  # If it's not the end
                        yield ('X-Wf-1-1-1-%d' % index, '|%s|\\' % (cut))
                        index += 1
                    else:  # If it's the end
                        yield ('X-Wf-1-1-1-%d' % index, '|%s|' % (cut))
                        index += 1
                        break

            else:
                yield ('X-Wf-1-1-1-%d' % index, '%d|%s|' % (len(code), code))
                index += 1
        yield ('X-Wf-1-Index', str(index - 1))
