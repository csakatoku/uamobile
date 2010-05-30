# -*- coding: utf-8 -*-
import re
from uamobile.scrapers.base import Scraper

class DoCoMoScraper(Scraper):
    url = 'http://www.nttdocomo.co.jp/service/imode/make/content/spec/screen_area/index.html'

    def do_scrape(self, doc):
        tables = [x for x in doc.xpath('//table') if x.attrib.get('summary', '').startswith(u'iモード')]

        res = {}
        for table in tables:
            imode2 = table.attrib.get('summary').startswith(u'iモードブラウザ2.0')
            for columns in table.xpath('tr'):
                if imode2:
                    model_index = 0
                    display_index = 4
                else:
                    if len(columns) == 6:
                        model_index = 0
                        display_index = 3
                    else:
                        model_index = 1
                        display_index = 4

                # model
                model_text = u''.join(columns[model_index].itertext()).strip()
                matcher = re.match(ur'([A-Z]{1,2})-?(\d{1,4}[a-zA-Z\u03bc]*)', model_text)
                if not matcher:
                    continue

                model = matcher.group(1) + matcher.group(2)
                if model.endswith(u'\u03bc'):
                    model = model[:-1] + 'myu'
                elif model.endswith(u'II'):
                    model = model[:-2] + '2'

                # height, width
                display_text = u''.join(columns[display_index].itertext())
                matcher = re.search(ur'(\d+).(\d+)', display_text)
                if not matcher:
                    continue

                width, height = map(int, matcher.groups())

                # color
                color_text = u''.join(columns[-1].itertext())
                color = color_text.startswith(u'カラー')

                # depth
                matcher = re.search(r'(\d+)', color_text)
                if matcher:
                    depth = int(matcher.group(1))
                else:
                    depth = 1

                res[model] = { 'width' : width,
                               'height': height,
                               'color' : color,
                               'depth' : depth,
                               }

        return res
