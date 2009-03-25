# -*- coding: utf-8 -*-
import re
from uamobile.utils import scraper

def test_cidr():
    def func(carrier):
        res = scraper.scrape_cidr(carrier)
        assert isinstance(res, list)
        for addr in res:
            assert isinstance(addr, str)
            assert re.match(r'^\d+\.\d+\.\d+\.\d+\/\d+$', addr)

    for s in ('docomo',
              'ezweb',
              'softbank',
              'willcom',
              ):
        yield func, s
