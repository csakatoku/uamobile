#!/usr/bin/env python
import re
import urllib
import pprint
from lxml import etree
from StringIO import StringIO

URL = 'http://www.nttdocomo.co.jp/service/imode/make/content/spec/screen_area/index.html'

MODEL_RE   = re.compile(r'^[A-Z]{1,2}\d+')
DISPLAY_RE = re.compile(r'[^\d]*(\d+)[^\d]+(\d+).*$', re.S)
COLOR_RE   = re.compile(r'[^\d]+(\d+)')

def build_displaymap():
    content = unicode(urllib.urlopen(URL).read(), 'cp932')

    for number, zenkaku in enumerate(u'\uff10\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19'):
        content = content.replace(zenkaku, str(number))

    tree = etree.parse(StringIO(content), etree.HTMLParser())

    displaymap = {}
    for node in tree.xpath('//tr[@class="acenter"]'):
        td = node.xpath('td')

        model = MODEL_RE.match(td[1][0].text) and td[1][0].text or td[0][0].text
        model = model.replace(u'\u03bc', u'myu').replace(u'\uff08', u' ').split()[0]

        display_text = u''.join(td[-3][0].itertext())
        width, height = DISPLAY_RE.match(display_text).groups()

        color_text = u''.join(td[-1][0].itertext())
        color = color_text.startswith(u'\u30ab\u30e9\u30fc')
        depth = COLOR_RE.match(color_text).group(1)

        displaymap[model.encode('ascii')] = dict(width=int(width),
                                                 height=int(height),
                                                 color=int(color),
                                                 depth=int(depth),
                                                 )

    return displaymap

if __name__ == '__main__':
    print "DISPLAYMAP_DOCOMO = %s" % pprint.pformat(build_displaymap())
