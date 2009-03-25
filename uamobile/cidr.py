# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from IPy import IP

from uamobile.cidrdata import crawler, docomo, ezweb, softbank, willcom

__all__ = ['IP', 'get_ip_addrs', 'get_ip']

def get_ip_addrs(carrier):
    carrier = carrier.lower()
    if carrier not in ('docomo', 'ezweb', 'softbank', 'willcom', 'crawler', 'nonmobile'):
        raise ValueError('invalid carrier name "%s"' % carrier)

    return { 'docomo'   : docomo.DATA,
             'ezweb'    : ezweb.DATA,
             'softbank' : softbank.DATA,
             'willcom'  : willcom.DATA,
             'crawler'  : crawler.DATA,
             'nonmobile': [ '0.0.0.0/0' ],
             }[carrier]

def get_ip(carrier, _memo={}):
    try:
        return _memo[carrier]
    except KeyError:
        _memo[carrier] = [IP(x) for x in get_ip_addrs(carrier)]
        return _memo[carrier]

