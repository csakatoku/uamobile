# -*- coding: utf-8 -*-
import re
import importlib

def test_cidr():
    def func(class_name):
        module_name, cls = class_name.rsplit('.', 1)
        module = importlib.import_module(module_name)

        instance = getattr(module, cls)()
        res = instance.scrape()

        assert isinstance(res, list)
        for addr in res:
            assert isinstance(addr, str), repr(addr)
            assert re.match(r'^\d+\.\d+\.\d+\.\d+\/\d+$', addr)

    for s in ('uamobile.scrapers.cidr.DoCoMoScraper',
              'uamobile.scrapers.cidr.EZWebScraper',
              'uamobile.scrapers.cidr.SoftBankScraper',
              'uamobile.scrapers.cidr.WILLCOMScraper',
              ):
        yield func, s
