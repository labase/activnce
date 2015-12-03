# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""

import re
import HTMLParser

def str_limit(str, size):
    return str if len(str) <= size else str[:size]+"..."

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    str = p.sub('', data)
    h = HTMLParser.HTMLParser()
    str = h.unescape(str)
    return str

def valid_latin1 (x, control=False):
    if control:
        return (x <= 126) or (x >= 160 and x <= 255)
    else:
        return (x >= 32 and x <= 126) or (x >= 160 and x <= 255)

def remove_non_latin1 (str, control=False):
    new_str = ''
    for i in range(len(str)):
        if valid_latin1(ord(str[i]), control):
            new_str = new_str + str[i]
    return (new_str)
    
    
def remove_diacritics(str):
    special_chars = [u'à', u'á', u'ã', u'â', u'À', u'Á', u'Ã', u'Â',\
                     u'é', u'ê', u'É', u'Ê',\
                     u'í', u'Í', \
                     u'ó', u'õ', u'ô', u'Ó',u'Õ', u'Ô', \
                     u'ú', u'ü', u'Ú', u'Ü', \
                     u'ç', u'Ç' ]
    chars = ['a', 'a', 'a', 'a', 'A', 'A', 'A', 'A',\
             'e', 'e', 'E', 'E',\
             'i',  'I', \
             'o', 'o', 'o', 'O', 'O', 'O', \
             'u', 'u', 'U', 'U', \
             'c', 'C' ]

    for i in range(len(special_chars)):
        str=str.replace(special_chars[i], chars[i])
           
    return str


def has_diacritics(str):
    for i in range(len(str)):
        if ord(str[i]) >= 128:
            return True
    return False


def remove_special_chars(str):
    strnew = ""
    for i in range(len(str)):
        if (str[i]>="A" and str[i]<="Z") or\
           (str[i]>="a" and str[i]<="z") or\
           (str[i]>="0" and str[i]<="9") or\
           (str[i]=="-") or\
           (str[i]=="_") or\
           (str[i]=="."):
            strnew += str[i]
            
    return strnew

def mem_size_format(str):
    try:
        size = int(str)
    except ValueError:
        return u'Valor não numérico!'
    units = ['bytes', 'kB', 'MB', 'GB', 'TB']
    
    i=0
    while size>1024 and i<4:
        i = i+1
        size = size/1024.0
       
    return "%.1f %s" % (size, units[i])
    