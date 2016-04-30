# encoding= utf-8

import re

xml_pattern = re.compile(r'xml version')


def isxml(txt):
    x = re.findall(xml_pattern, txt)
    if x:
        return True
    else:
        return False
