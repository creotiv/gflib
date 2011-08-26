__all__ = ['xmltodict','ParseXML']

import logging
try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    raise Exception("Failed to import ElementTree from any known place")


def xmltodict(node):
    if len(node):
        if node[0].tag == node.tag[:-1]:
            res = []
            t   = 1
        else:
            res = {}
            t   = 2
        for n in node:
            if not isinstance(n.tag,str):
                continue
            if t == 1:
                val = xmltodict(n)
                if isinstance(val,dict):
                    val.update(n.attrib)
                elif not val:
                    val = dict(n.attrib)
                res.append(val)
            elif t == 2:
                val = xmltodict(n)
                if isinstance(val,dict):
                    val.update(n.attrib)
                elif not val:
                    val = dict(n.attrib)
                res[n.tag] = val
        
    else:
        res = node.text
        if res:
            res = res.strip()
        else:
            res = ''
    return res
        
def ParseXML(fname,sname=None): 
    tree = etree.parse(fname)
    if sname:
        xmlschema_doc = etree.parse(sname)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not xmlschema.validate(tree):
            errors = []
            for i,e in enumerate(xmlschema.error_log):
                errors.append('%s) %s\n' % (i+1,e))
            return False,errors
    return xmltodict(tree.getroot()),[]
   

    
    
