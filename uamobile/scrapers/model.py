# -*- coding: utf-8 -*-
from uamobile.scrapers.base import Scraper

class EZWebScraper(Scraper):
    url = 'http://www.au.kddi.com/ezfactory/tec/spec/4_4.html'

    def do_scrape(self, doc):
        tables = doc.xpath('//table[@cellspacing="1"]')
        res = []
        for table in tables[1:]:
            for idx, tr in enumerate(table.xpath('tr')):
                if idx == 0:
                    continue

                for key, value in zip(tr[0::2], tr[1::2]):
                    models = ''.join(key.itertext()).strip().split('/')
                    devices = ''.join(value.itertext()).strip().split('/')

                    for device in devices:
                        if not device:
                            continue

                        for idx, model in enumerate(models):
                            if not model:
                                continue

                            if idx == 0:
                                res.append((device, unicode(model)))
                            else:
                                pos = models[0].find(model[0])
                                model_name = models[0][:pos] + model
                                res.append((device, unicode(model_name)))
        return res
