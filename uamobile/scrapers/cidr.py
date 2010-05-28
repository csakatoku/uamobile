# -*- coding: utf-8 -*-
from uamobile.scrapers.base import Scraper

class DoCoMoScraper(Scraper):
    url = 'http://www.nttdocomo.co.jp/service/imode/make/content/ip/'

    def do_scrape(self, doc):
        return [x.text for x in doc.xpath('//div[@class="boxArea" and count(preceding-sibling::*)=2]/div/div[@class="section"]/ul[@class="normal txt" and position()=1]/li')]


class EZWebScraper(Scraper):
    url = 'http://www.au.kddi.com/ezfactory/tec/spec/ezsava_ip.html'

    def do_scrape(self, doc):
        res = []
        rows = doc.xpath("""//table[@cellspacing="1"]/tr[@bgcolor="#ffffff"]""")
        for row in rows:
            cols = row.xpath('./td/div[@class="TableText"]/text()')
            if len(cols) == 4:
                # deprecated
                continue
            res.append('%s%s' % (cols[1], cols[2]))
        return res


class SoftBankScraper(Scraper):
    url = 'http://creation.mb.softbank.jp/web/web_ip.html'

    def do_scrape(self, doc):
        return [x.text.strip() for x in doc.xpath("//div[@class='contents']/table/tr[7]/td/table/tr/td/table/tr/td")]


class WILLCOMScraper(Scraper):
    url = 'http://www.willcom-inc.com/ja/service/contents_service/create/center_info/index.html'

    def do_scrape(self, doc):
        res = []
        sep = 0
        for td in doc.xpath("//table[@width='100%' and @cellspacing='1' and @cellpadding='3']/tr/td"):
            if td.attrib.get('colspan') == "4":
                sep += 1
                if sep > 1:
                    break
            else:
                if td.attrib.get('align') == 'center' and td.attrib.get('bgcolor') == 'white':
                    txt = td[0].text
                    if txt:
                        res.append(txt)
        return res
