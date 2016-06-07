# encoding= utf-8

import re

xml_pattern = re.compile(r'(<\?xml[^>]+>\s*<msg .*></msg>)', re.DOTALL)  # re.DOTALL指定'.'可以匹配换行符


def isxml(txt):
    x = re.findall(xml_pattern, txt)
    if x:
        return True
    else:
        return False


def getXML(txt):
    xml = re.findall(xml_pattern, txt)
    txt = re.sub(xml_pattern, '', txt)
    return xml[0], txt
