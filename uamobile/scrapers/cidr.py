# -*- coding: utf-8 -*-
import urllib2
from lxml import etree

class CIDR(object):
    # subclass must override this property
    url = None

    def scrape(self):
        stream = self.get_stream()
        doc = etree.parse(stream, etree.HTMLParser())
        res = []
        for addr in self.do_scrape(doc):
            res.append(str(addr))
        return res

    def get_stream(self):
        return urllib2.urlopen(self.url)

    def do_scrape(self, doc):
        raise NotImplementedError()


class DoCoMoCIDR(CIDR):
    url = 'http://www.nttdocomo.co.jp/service/imode/make/content/ip/'

    def do_scrape(self, doc):
        return [x.text for x in doc.xpath('//div[@class="boxArea" and count(preceding-sibling::*)=2]/div/div[@class="section"]/ul[@class="normal txt" and position()=1]/li')]


class EZWebCIDR(CIDR):
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


class SoftBankCIDR(CIDR):
    url = 'http://creation.mb.softbank.jp/web/web_ip.html'

    def do_scrape(self, doc):
        return [x.text.strip() for x in doc.xpath("//div[@class='contents']/table/tr[7]/td/table/tr/td/table/tr/td")]


class WILLCOMCIDR(CIDR):
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


def scrape_cidr(carrier):
    carrier = carrier.lower()

    alias = { 'kddi'      : 'ezweb',
              'thirdforce': 'softbank',
              }.get(carrier)
    if alias is not None:
        carrier = alias

    try:
        s = { 'docomo'  : DoCoMoCIDR(),
              'ezweb'   : EZWebCIDR(),
              'softbank': SoftBankCIDR(),
              'willcom' : WILLCOMCIDR(),
              }[carrier]
        return s.scrape()
    except KeyError:
        raise ValueError('invalid carrier name "%s"' % carrier)
