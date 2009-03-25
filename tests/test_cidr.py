# -*- coding: utf-8 -*-
from uamobile import cidr

def test_get_ip_addrs():
    def func(carrier):
        addrs = cidr.get_ip_addrs(carrier)
        assert isinstance(addrs, list)
        for addr in addrs:
            assert isinstance(addr, str)

    for c in ('docomo',
              'ezweb',
              'softbank',
              'willcom',
              'crawler',
              'nonmobile',
              # case insensitive
              'DoCoMo',
              'EZWeb',
              'SoftBank',
              'WILLCOM',
              'Crawler',
              'NonMobile',
              ):
        yield func, c

def test_get_ip_addrs_error():
    try:
        cidr.get_ip_addrs('spam')
    except ValueError:
        pass
    else:
        assert False

def test_get_ip():
    def func(carrier):
        addrs = cidr.get_ip(carrier)
        assert isinstance(addrs, list)
        for addr in addrs:
            assert isinstance(addr, cidr.IP)

    for c in ('docomo',
              'ezweb',
              'softbank',
              'willcom',
              'crawler',
              'nonmobile',
              # case insensitive
              'DoCoMo',
              'EZWeb',
              'SoftBank',
              'WILLCOM',
              'Crawler',
              'NonMobile',
              ):
        yield func, c

def test_get_ip_addrs_error():
    try:
        cidr.get_ip('spam')
    except ValueError:
        pass
    else:
        assert False
