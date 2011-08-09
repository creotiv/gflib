#!/usr/bin/env python

"""Escaping/unescaping methods for HTML, JSON, URLs, and others."""

import htmlentitydefs
import xml.sax.saxutils
import urllib

try:
    import simplejson
    _json_decode = lambda s: simplejson.loads(_unicode(s))
    _json_encode = lambda v: simplejson.dumps(v)
except ImportError:
    try:
        import json
        assert hasattr(json, "loads") and hasattr(json, "dumps")
        _json_decode = lambda s: json.loads(s)
        _json_encode = lambda v: json.dumps(v)
    except:
        try:
            # For Google AppEngine
            from django.utils import simplejson
            _json_decode = lambda s: simplejson.loads(_unicode(s))
            _json_encode = lambda v: simplejson.dumps(v)
        except ImportError:
            raise Exception("A JSON parser is required, e.g., simplejson at "
                            "http://pypi.python.org/pypi/simplejson/")

def html_unescape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&quot;','"').replace('&#39;',"'")

def xhtml_escape(value):
    """Escapes a string so it is valid within XML or XHTML."""
    return utf8(xml.sax.saxutils.escape(value))


def xhtml_unescape(value):
    """Un-escapes an XML-escaped string."""
    return re.sub(r"&(#?)(\w+?);", _convert_entity, _unicode(value))


def json_encode(value):
    """JSON-encodes the given Python object."""
    return _json_encode(value)


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return _json_decode(value)


def squeeze(value):
    """Replace all sequences of whitespace chars with a single space."""
    return re.sub(r"[\x00-\x20]+", " ", value).strip()


def url_escape(value,safe=None):
    """Returns a valid URL-encoded version of the given value."""
    return urllib.quote_plus(utf8(value),safe)

def url_quote(value):
    """Returns a valid URL-encoded version of the given value."""
    return urllib.urlencode({"":utf8(value)})[1:]

def url_unescape(value):
    """Decodes the given value from a URL."""
    return _unicode(urllib.unquote_plus(value))


def utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value


def _unicode(value):
    if isinstance(value, str):
        return value.decode("utf-8")
    assert isinstance(value, unicode)
    return value


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return unichr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return "&%s;" % m.group(2)


def _build_unicode_map():
    unicode_map = {}
    for name, value in htmlentitydefs.name2codepoint.iteritems():
        unicode_map[name] = unichr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()
