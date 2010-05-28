# -*- coding: utf-8 -*-
import urllib2
from lxml import etree

class Scraper(object):
    # subclass must override this property
    url = None

    def scrape(self):
        stream = self.get_stream()
        doc = self.get_document(stream)
        return self.do_scrape(doc)

    def get_document(self, stream):
        doc = etree.parse(stream, etree.HTMLParser())
        return doc

    def get_stream(self):
        return urllib2.urlopen(self.url)

    def do_scrape(self, doc):
        raise NotImplementedError()

