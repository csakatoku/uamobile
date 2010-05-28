# -*- coding: utf-8 -*-
import re
from uamobile.scrapers.base import Scraper

class DoCoMoScraper(Scraper):
    url = 'http://www.nttdocomo.co.jp/service/imode/make/content/spec/flash/'

    def do_scrape(self, doc):
        tables = [x for x in doc.xpath('//table') if x.attrib.get('summary', '').startswith('Flash')]

        res = {}
        for table, version in zip(tables, ('1.0', '1.1', '3.0', '3.1')):
            for columns in table.xpath('tr'):
                if len(columns) == 9:
                    span = columns[0].find("span")
                elif len(columns) == 10:
                    span = columns[1].find("span")
                else:
                    continue

                model = span.text.strip()
                matcher = re.match(ur'([A-Z]{1,2})-?(\d{1,3}[a-zA-Z\u03bc]+)', model)
                if not matcher:
                    print model
                    continue

                model = matcher.group(1) + matcher.group(2)
                if model.endswith(u'\u03bc'):
                    model = model[:-1] + 'myu'

                res[str(model)] = version

        return res


class EZWebScraper(Scraper):
    url = 'http://www.au.kddi.com/ezfactory/tec/spec/new_win/ezkishu.html'

    def get_model(self, name):
        from uamobile.data.model.ezweb import DATA
        for k, v in DATA:
            if v == name:
                return k
        return None

    def do_scrape(self, doc):
        tables = doc.xpath('//table[@width="892"]')
        res = {}
        for table in tables:
            for tr in table.xpath('tr'):
                if tr[0].attrib.get('bgcolor') != '#f2f2f2':
                    continue

                flash = ''.join(tr[11].itertext()).strip()
                if flash == u'\u25cf':
                    version = '2.0'
                elif flash == u'\u25ce':
                    version = '1.1'
                elif flash == u'\u25cb':
                    version = '1.1'
                else:
                    continue

                devices = ''.join(tr[0].itertext()).strip().split('/')
                for idx, device in enumerate(devices):
                    if not device:
                        continue

                    if idx == 0:
                        model = self.get_model(device)
                    else:
                        pos = devices[0].find(device[0])
                        model = self.get_model(devices[0][:pos] + device)

                    if not model:
                        continue

                    res[model] = version

        return res

class SoftBankScraper(Scraper):
    url = 'http://creation.mb.softbank.jp/terminal/?lup=y&cat=service'

    def get_document(self, stream):
        return stream.read()

    def do_scrape(self, doc):
        res = {}
        tr = re.findall(r'<td width="(?:6|14)%">(.+?)</td>', doc)
        for model, flash in zip(tr[0::2], tr[1::2]):
            matcher = re.search(r'(\d\.\d)$', flash)
            if matcher:
                version = matcher.group(1)
            else:
                continue

            matcher = re.search(r'^(\d+[A-Z]{1,2}|DM\d+[A-Z]{1,2})', model)
            if matcher:
                model = matcher.group(1)
            else:
                continue

            res[model] = version

        return res
