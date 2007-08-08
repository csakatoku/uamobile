# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display

import re
from cStringIO import StringIO

try:
    from xml.etree.cElementTree import iterparse
except ImportError:
    try:
        from cElementTree import iterparse
    except ImportError:
        from ElementTree import iterparse

COMMENT_RE = re.compile(r'^\((.*)\)$')
CACHE_RE = re.compile(r'^c(\d+)')

SERIALNUMBER_RE = re.compile(r'^ser(\w{11})$')
STATUS_RE = re.compile(r'^(T[CDBJ])$')
BANDWIDTH_RE = re.compile(r'^s(\d+)$')
DISPLAY_BITES_RE = re.compile(r'^W(\d+)H(\d+)$')
VENDOR_RE = re.compile(r'([A-Z]+)\d')

FOMA_PARAMS_START_RE = re.compile(r'^([^(]+)')
FOMA_PARAMS_RE = re.compile(r'^[^(]+\((.*?)\)$')
FOMA_CACHE_RE = re.compile(r'^c(\d+)$')
FOMA_SERIALNUMBER_RE = re.compile(r'^ser(\w{15})$')
FOMA_STATUS_RE = re.compile(r'^(T[CDBJ])$')
FOMA_CARDID_RE = re.compile(r'^icc(\w{20})?$')
FOMA_DISPLAY_BYTES_RE = re.compile(r'^W(\d+)H(\d+)$')
FOMA_SERIES_4DIGITS_RE = re.compile(r'(\d{4})')
FOMA_SERIES_3DIGITS_RE = re.compile(r'(\d{3}i)')

class DoCoMoUserAgent(UserAgent):
    """
    NTT DoCoMo implementation
    see also http://www.nttdocomo.co.jp/service/imode/make/content/spec/useragent/index.html
    """
    carrier = 'DoCoMo'
    short_carrier = 'D'

    HTML_VERSION_MAP = (((re.compile('[DFNP]501i'), '1.0'),
                         (re.compile('502i|821i|209i|651|691i|(F|N|P|KO)210i|^F671i$'), '2.0'),
                         (re.compile('(D210i|SO210i)|503i|211i|SH251i|692i|200[12]|2101V'), '3.0'),
                         (re.compile('504i|251i|^F671iS$|212i|2051|2102V|661i|2701|672i|SO213i|850i'), '4.0'),
                         (re.compile('eggy|P751v'), '3.2'),
                         (re.compile('505i|252i|900i|506i|880i|253i|P213i|901i|700i|851i|701i|881i|^SA800i$|600i|^L601i$|^M702i(S|G)$'), '5.0'),
                         (re.compile('902i|702i|851i|882i|^N601i$|^D800iDS$|^P703imyu$'), '6.0'),
                         (re.compile('903i|703i|904i|704i'), '7.0')
                         ))

    def __init__(self, *args, **kwds):
        UserAgent.__init__(self, *args, **kwds)
        self.model = ''
        self._status = ''
        self.bandwidth = None
        self.serialnumber = None
        self.card_id = None
        self.comment = None
        self._cache_size = None
        self._display_bytes = ''
        self._is_foma = False

    def is_docomo(self):
        return True

    def get_html_version(self):
        """
        returns supported HTML version like '3.0'.
        if unkwon, return None.
        """
        for pattern, value in self.HTML_VERSION_MAP:
            if pattern.search(self.model):
                return value
        return None
    html_version = property(get_html_version)
        
    def get_cache_size(self):
        """
        returns cache size as kilobytes unit.
        return 5 if unkwon.
        """
        if self._cache_size:
            return self._cache_size

        return 5
    cache_size = property(get_cache_size)

    def get_vendor(self):
        """
        returns vender code like 'SO' for Sony.
        if unkwon, returns None
        """
        matcher = VENDOR_RE.match(self.model)
        if matcher:
            return matcher.group(1)
        else:
            return None
    vendor = property(get_vendor)

    def get_series(self):
        """
        returns series name like '502i'.
        if unknow, return None.
        """
        if self._is_foma and FOMA_SERIES_4DIGITS_RE.search(self.model):
            return 'FOMA'
    
        matcher = FOMA_SERIES_3DIGITS_RE.search(self.model)
        if matcher:
            return matcher.group(1)

        if self.model == 'P651ps':
            return '651'

        return None
    series = property(get_series)

    def get_status(self):
        """
        returns status like "TB", "TC", "TD", or "TJ", which means:
        TB | Browsers
        TC | Browsers with image off (only Available in HTTP 5.0)
        TD | Fetching JAR
        TJ | i-Appli
        """
        return self._status
    status = property(get_status)

    def is_gps(self):
        return self.model in ('F661i', 'F505iGPS')

    def is_foma(self):
        return self._is_foma

    def is_cookie_available(self):
        return False

    def make_display(self):
        """
        create a new Display object.
        """
        info = get_map(self.model)
        return Display(info)

    def parse(self):
        main, foma_or_comment = (self.useragent.split(' ', 1) + [None])[:2]
        if foma_or_comment:
            matcher = COMMENT_RE.match(foma_or_comment)
            if matcher:
                # DoCoMo/1.0/P209is (Google CHTML Proxy/1.0)
                self.comment = matcher.group(1)
                result = self._parse_main(main)
            else:
                # DoCoMo/2.0 N2001(c10;ser0123456789abcde;icc01234567890123456789)
                self._is_foma = True
                self._name, self._version = main.split('/')
                result = self._parse_foma(foma_or_comment)
        else:
            # DoCoMo/1.0/R692i/c10
            result = self._parse_main(main)

        return result

    def _parse_main(self, main):
        """
        parse main part of HTTP_USER_AGENT string (not foma)
        """
        self._name, self._version, self.model, cache, rest = (main.split('/', 4) + [None, None, None, None])[:5]
        if self.model == 'SH505i2':
            self.model = 'SH505i'

        if cache:
            matcher = CACHE_RE.match(cache)
            if not matcher:
                raise exceptions.NoMatchingError(self)
            self._cache_size = int(matcher.group(1))

        if rest:
            for value in rest.split('/'):
                matcher = SERIALNUMBER_RE.match(value)
                if matcher:
                    self.serialnumber = matcher.group(1)
                    continue
                
                matcher = BANDWIDTH_RE.match(value)
                if matcher:
                    self.bandwidth = int(matcher.group(1))
                    continue

                matcher = STATUS_RE.match(value)
                if matcher:
                    self._status = matcher.group(1)
                    continue

                matcher = DISPLAY_BITES_RE.match(value)
                if matcher:
                    self._display_bytes = '%s*%s' % (matcher.group(1),
                                                     matcher.group(2))

    def _parse_foma(self, foma):
        matcher = FOMA_PARAMS_START_RE.match(foma)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        self.model = matcher.group(1)
        if self.model == 'MST_v_SH2101V':
            self.model = 'SH2101V'

        matcher = FOMA_PARAMS_RE.match(foma)
        if matcher:
            for value in matcher.group(1).split(';'):
                matcher = FOMA_CACHE_RE.match(value)
                if matcher:
                    self._cache_size = int(matcher.group(1))
                    continue

                matcher = FOMA_SERIALNUMBER_RE.match(value)
                if matcher:
                    self.serialnumber = matcher.group(1)
                    continue

                matcher = FOMA_STATUS_RE.match(value)
                if matcher:
                    self._status = matcher.group(1)
                    continue
                
                matcher = FOMA_CARDID_RE.match(value)
                if matcher:
                    self.card_id = matcher.group(1)
                    continue
                
                matcher = FOMA_DISPLAY_BYTES_RE.match(value)
                if matcher:
                    self._display_bytes = '%s*%s' % (matcher.group(1),
                                                     matcher.group(2))
                    continue

                raise exceptions.NoMatchingError(self)

#########################################
# Display information mapping for DoCoMo
#########################################

def get_map(model, maps={}):
    map = maps.setdefault('default', _parse_display_map(StringIO(_DEFAULT_DISPLAY_MAP_DATA)))
    return map.get(model)

def _parse_display_map(fp):
    map = {}
    for evt, el in iterparse(fp):
        if el.tag != 'opt':
            map[el.tag] = { 'color' : el.attrib['color'],
                            'depth' : el.attrib['depth'],
                            'height': el.attrib['height'],
                            'width' : el.attrib['width'] }
    return map

_DEFAULT_DISPLAY_MAP_DATA = """<?xml version="1.0" ?>
<opt>
  <D209I color="1" depth="256" height="90" width="96" />
  <D2101V color="1" depth="262144" height="130" width="120" />
  <D210I color="1" depth="256" height="91" width="96" />
  <D211I color="1" depth="4096" height="91" width="100" />
  <D251I color="1" depth="262144" height="144" width="132" />
  <D251IS color="1" depth="262144" height="144" width="132" />
  <D252I color="1" depth="262144" height="198" width="176" />
  <D253I color="1" depth="262144" height="198" width="176" />
  <D253IWM color="1" depth="262144" height="144" width="220" />
  <D501I color="" depth="2" height="72" width="96" />
  <D502I color="1" depth="256" height="90" width="96" />
  <D503I color="1" depth="4096" height="126" width="132" />
  <D503IS color="1" depth="4096" height="126" width="132" />
  <D504I color="1" depth="262144" height="144" width="132" />
  <D505I color="1" depth="262144" height="270" width="240" />
  <D505IS color="1" depth="262144" height="270" width="240" />
  <D506I color="1" depth="262144" height="270" width="240" />
  <D900I color="1" depth="262144" height="270" width="240" />
  <D901I color="1" depth="262144" height="240" width="230" />
  <D901IS color="1" depth="262144" height="240" width="230" />
  <ER209I color="" depth="2" height="72" width="120" />
  <F2051 color="1" depth="65536" height="182" width="176" />
  <F209I color="1" depth="256" height="91" width="96" />
  <F2102V color="1" depth="65536" height="182" width="176" />
  <F210I color="1" depth="256" height="113" width="96" />
  <F211I color="1" depth="4096" height="113" width="96" />
  <F212I color="1" depth="65536" height="136" width="132" />
  <F251I color="1" depth="65536" height="140" width="132" />
  <F501I color="" depth="2" height="84" width="112" />
  <F502I color="1" depth="256" height="91" width="96" />
  <F502IT color="1" depth="256" height="91" width="96" />
  <F503I color="1" depth="256" height="130" width="120" />
  <F503IS color="1" depth="4096" height="130" width="120" />
  <F504I color="1" depth="65536" height="136" width="132" />
  <F504IS color="1" depth="65536" height="136" width="132" />
  <F505I color="1" depth="262144" height="268" width="240" />
  <F505IGPS color="1" depth="262144" height="268" width="240" />
  <F506I color="1" depth="262144" height="268" width="240" />
  <F661I color="1" depth="65536" height="136" width="132" />
  <F671I color="1" depth="256" height="126" width="120" />
  <F671IS color="1" depth="65536" height="120" width="160" />
  <F672I color="1" depth="65536" height="120" width="160" />
  <F700I color="1" depth="262144" height="240" width="230" />
  <F880IES color="1" depth="65536" height="256" width="240" />
  <F900I color="1" depth="262144" height="240" width="230" />
  <F900IC color="1" depth="262144" height="240" width="230" />
  <F900IT color="1" depth="262144" height="240" width="230" />
  <F901IC color="1" depth="262144" height="240" width="230" />
  <F901IS color="1" depth="262144" height="240" width="230" />
  <KO209I color="1" depth="256" height="96" width="96" />
  <KO210I color="1" depth="256" height="96" width="96" />
  <N2001 color="1" depth="4096" height="128" width="118" />
  <N2002 color="1" depth="65536" height="128" width="118" />
  <N2051 color="1" depth="65536" height="198" width="176" />
  <N209I color="" depth="4" height="82" width="108" />
  <N2102V color="1" depth="65536" height="198" width="176" />
  <N210I color="1" depth="256" height="113" width="118" />
  <N211I color="1" depth="4096" height="128" width="118" />
  <N211IS color="1" depth="4096" height="128" width="118" />
  <N251I color="1" depth="65536" height="140" width="132" />
  <N251IS color="1" depth="65536" height="140" width="132" />
  <N252I color="1" depth="65536" height="140" width="132" />
  <N253I color="1" depth="65536" height="180" width="160" />
  <N2701 color="1" depth="65536" height="198" width="176" />
  <N501I color="" depth="2" height="128" width="118" />
  <N502I color="" depth="4" height="128" width="118" />
  <N502IT color="1" depth="256" height="128" width="118" />
  <N503I color="1" depth="4096" height="128" width="118" />
  <N503IS color="1" depth="4096" height="128" width="118" />
  <N504I color="1" depth="65536" height="180" width="160" />
  <N504IS color="1" depth="65536" height="180" width="160" />
  <N505I color="1" depth="262144" height="270" width="240" />
  <N505IS color="1" depth="262144" height="270" width="240" />
  <N506I color="1" depth="262144" height="295" width="240" />
  <N506IS color="1" depth="262144" height="295" width="240" />
  <N700I color="1" depth="65536" height="270" width="240" />
  <N821I color="" depth="4" height="128" width="118" />
  <N900I color="1" depth="65536" height="269" width="240" />
  <N900IG color="1" depth="65536" height="269" width="240" />
  <N900IL color="1" depth="65536" height="269" width="240" />
  <N900IS color="1" depth="65536" height="269" width="240" />
  <N901IC color="1" depth="65536" height="270" width="240" />
  <N901IS color="1" depth="65536" height="270" width="240" />
  <NM502I color="" depth="2" height="106" width="111" />
  <P2002 color="1" depth="65536" height="128" width="118" />
  <P209I color="" depth="4" height="87" width="96" />
  <P209IS color="1" depth="256" height="87" width="96" />
  <P2101V color="1" depth="262144" height="182" width="163" />
  <P2102V color="1" depth="262144" height="198" width="176" />
  <P210I color="1" depth="256" height="91" width="96" />
  <P211I color="1" depth="65536" height="130" width="120" />
  <P211IS color="1" depth="65536" height="130" width="120" />
  <P213I color="1" depth="65536" height="144" width="132" />
  <P251IS color="1" depth="65536" height="144" width="132" />
  <P252I color="1" depth="65536" height="144" width="132" />
  <P252IS color="1" depth="65536" height="144" width="132" />
  <P253I color="1" depth="65536" height="144" width="132" />
  <P253IS color="1" depth="65536" height="144" width="132" />
  <P501I color="" depth="2" height="120" width="96" />
  <P502I color="" depth="4" height="117" width="96" />
  <P503I color="1" depth="256" height="130" width="120" />
  <P503IS color="1" depth="256" height="130" width="120" />
  <P504I color="1" depth="65536" height="144" width="132" />
  <P504IS color="1" depth="65536" height="144" width="132" />
  <P505I color="1" depth="65536" height="266" width="240" />
  <P505IS color="1" depth="65536" height="266" width="240" />
  <P506IC color="1" depth="65536" height="266" width="240" />
  <P651PS color="" depth="4" height="87" width="96" />
  <P700I color="1" depth="65536" height="270" width="240" />
  <P821I color="" depth="4" height="128" width="118" />
  <P900I color="1" depth="65536" height="266" width="240" />
  <P900IV color="1" depth="262144" height="266" width="240" />
  <P901I color="1" depth="65536" height="270" width="240" />
  <P901IS color="1" depth="65536" height="270" width="240" />
  <R209I color="" depth="4" height="72" width="96" />
  <R211I color="1" depth="4096" height="98" width="96" />
  <R691I color="" depth="4" height="72" width="96" />
  <R692I color="1" depth="4096" height="98" width="96" />
  <SH2101V color="1" depth="65536" height="600" width="800" />
  <SH251I color="1" depth="65536" height="130" width="120" />
  <SH251IS color="1" depth="65536" height="187" width="176" />
  <SH252I color="1" depth="262144" height="252" width="240" />
  <SH505I color="1" depth="262144" height="252" width="240" />
  <SH505IS color="1" depth="262144" height="252" width="240" />
  <SH506IC color="1" depth="262144" height="252" width="240" />
  <SH700I color="1" depth="262144" height="252" width="240" />
  <SH821I color="1" depth="256" height="78" width="96" />
  <SH900I color="1" depth="262144" height="252" width="240" />
  <SH901IC color="1" depth="262144" height="252" width="240" />
  <SH901IS color="1" depth="262144" height="252" width="240" />
  <SO210I color="1" depth="256" height="113" width="120" />
  <SO211I color="1" depth="4096" height="112" width="120" />
  <SO212I color="1" depth="65536" height="112" width="120" />
  <SO213I color="1" depth="65536" height="112" width="120" />
  <SO213IS color="1" depth="65536" height="112" width="120" />
  <SO502I color="" depth="4" height="120" width="120" />
  <SO502IWM color="1" depth="256" height="113" width="120" />
  <SO503I color="1" depth="65536" height="113" width="120" />
  <SO503IS color="1" depth="65536" height="113" width="120" />
p  <SO504I color="1" depth="65536" height="112" width="120" />
  <SO505I color="1" depth="262144" height="240" width="256" />
  <SO505IS color="1" depth="262144" height="256" width="240" />
  <SO506I color="1" depth="262144" height="256" width="240" />
  <SO506IC color="1" depth="262144" height="256" width="240" />
  <SO506IS color="1" depth="262144" height="256" width="240" />
  <T2101V color="1" depth="262144" height="144" width="176" />
</opt>"""

if __name__ == '__main__':
    from cStringIO import StringIO
    print _parse_display_map(StringIO(_DEFAULT_DISPLAY_MAP_DATA))
