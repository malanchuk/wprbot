# -*- coding: utf-8 -*-
"""
Simple set of string processors
"""

import re
import random
from unidecode import unidecode
from lxml import etree
from urllib.parse import urlparse, parse_qs, urlencode



def replace_umlauts(text):
    umlauts = {'ä': 'ae','ö': 'oe','ü': 'ue', 'ß': 'ss', 
               'Ä': 'Ae','Ö': 'Oe','Ü': 'Ue', }
    for um,r in umlauts.items():
        text = text.replace(um, r)
    text = unidecode(text)
    return text


def clean_punct(text, replace_char=''):
    """ Remove punctuation chars from string
    """
    punctuation = '!"$%\'()*,.:;<=>?@[\\]^_`-/'
    for p in punctuation:
        text = text.replace(p, replace_char)

    return text.lower().replace('\n', ' ')


def s_format(s, if_none=None):
    """Converts string to readable format
    """
    if not s:
        return if_none
    s = re.sub('\s+', ' ', s)
    s = re.sub('<[^<]+?>', '  ', s)
    s = re.sub('\s{2,}', '\n\n', s)
    s = re.sub('^\s+', '', s)

    return s.strip()


def clean_space(s, if_none=''):
    """Remove html and extra spaces.
    """
    if not s:
        return if_none
    s = re.sub('(<[^<]+?>|&.{0,}?;)', '', re.sub('[\r\n\t]*\s{2,}', ' ', s)).strip()
    s = u" ".join(s.split())

    return s or if_none


def n_format(s, integer=False, if_none=''):
    """Convert string to a number format
    """
    if not s:
        return if_none
    try:    
        s = re.sub('[^\d\.,]', '', s).strip('.,')
        lpart = s
        rpart = ''
        if re.search('(\.|,)\d{1,2}$', s):
            lpart = lpart.replace(re.search('(\.|,)(\d{1,2})$', s).group(), '')
            rpart = ',' + re.search('(\.|,)(\d{1,2})$', s).group(2)
    except AttributeError:
        return if_none
    lpart = re.sub('[^\d]+', '', lpart)
    if integer:
        try:
            return int(lpart)
        except ValueError:
            return if_none
    return (lpart+rpart) or if_none


def safe_index(l, i=0):
    """Safely extract value from list
    """
    try:
        return l[i]
    except (IndexError, TypeError):
        return ''

def clean_scripts(root):
    path = '//script|//head|//style'
    page_dom = root
    while page_dom.xpath(path):
        page_dom.xpath(path)[0].getparent()\
                .remove(page_dom.xpath(path)[0])


def tostring(root):
    """ Make unicode string from lxml Element
    """
    return etree.tostring(root, encoding='UTF-8').decode('utf-8')


def clean_url(url):
    u = urlparse(url)
    query = parse_qs(u.query)
    for qkey in list(query.keys()):
        if re.search(r'(?i)sess|sid', qkey):
            query.pop(qkey)
    u = u._replace(query=urlencode(query, True))
    u = u._replace(params='')
    return u.geturl()

def clean_phone(phone):
    """ Remove all extra char from phone
    """    
    phone = re.sub('[^\d]', '', phone or '').strip()    
    return phone    

def uncrypt_typo3_email(enc):
    """ Deopfuscate email
    """    
    def decryptCharcode(n,start,end,offset):
        n = n + offset;
        if offset > 0 and n > end:
            n = start + (n - end - 1)
        elif offset < 0 and n < start:
            n = end - (start - n - 1)
        return chr(n);
    offset = ord('m') - ord(enc[0])
    dec = "";
    for char in enc:
        n = ord(char)
        if (n >= 0x2B and n <= 0x3A):
            dec += decryptCharcode(n,0x2B,0x3A,offset)
        elif (n >= 0x40 and n <= 0x5A):
            dec += decryptCharcode(n,0x40,0x5A,offset)
        elif (n >= 0x61 and n <= 0x7A):
            dec += decryptCharcode(n,0x61,0x7A,offset)
        else:
            dec += char;
    return dec;
