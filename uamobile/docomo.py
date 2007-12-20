# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display
from uamobile.docomodisplaymap import DISPLAYMAP_DOCOMO

import re

try:
    frozenset
except NameError:
    from sets import Set as frozenset

STATUS_SET = frozenset(['TC', 'TD', 'TB', 'TJ'])

DISPLAY_BYTES_RE = re.compile(r'^W(\d+)H(\d+)$')
VENDOR_RE = re.compile(r'([A-Z]+)\d')

FOMA_SERIES_4DIGITS_RE = re.compile(r'\d{4}')
FOMA_SERIES_3DIGITS_RE = re.compile(r'(\d{3}i)')

class DoCoMoUserAgent(UserAgent):
    """
    NTT DoCoMo implementation
    see also http://www.nttdocomo.co.jp/service/imode/make/content/spec/useragent/index.html

    property "cache" returns cache size as kilobytes unit.

    property "status" means:
    TB | Browsers
    TC | Browsers with image off (only Available in HTTP 5.0)
    TD | Fetching JAR
    TJ | i-Appli
    """
    carrier = 'DoCoMo'
    short_carrier = 'D'

    HTML_VERSION_MAP = (((re.compile('[DFNP]501i'), '1.0'),
                         (re.compile('502i|821i|209i|651|691i|(?:F|N|P|KO)210i|^F671i$'), '2.0'),
                         (re.compile('(?:D210i|SO210i)|503i|211i|SH251i|692i|200[12]|2101V'), '3.0'),
                         (re.compile('504i|251i|^F671iS$|212i|2051|2102V|661i|2701|672i|SO213i|850i'), '4.0'),
                         (re.compile('eggy|P751v'), '3.2'),
                         (re.compile('505i|252i|900i|506i|880i|253i|P213i|901i|700i|851i$|701i|881i|^SA800i$|600i|^L601i$|^M702i(?:S|G)$|^L602i$'), '5.0'),
                         (re.compile('902i|702i|851iWM|882i|883i$|^N601i$|^D800iDS$|^P70[34]imyu$'), '6.0'),
                         (re.compile('883iES|903i|703i|904i|704i'), '7.0'),
                         (re.compile('905i'), '7.1'),
                         ))

    def __init__(self, *args, **kwds):
        UserAgent.__init__(self, *args, **kwds)
        self.model = ''
        self.version = ''
        self.bandwidth = None
        self.serialnumber = None
        self.card_id = None
        self.comment = None
        self.cache_size = 5
        self._display_bytes = None
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

    def is_gps(self):
        return self.model in ('F661i', 'F505iGPS')

    def is_foma(self):
        return self._is_foma

    def supports_cookie(self):
        return False

    def make_display(self):
        """
        create a new Display object.
        """
        try:
            params = DISPLAYMAP_DOCOMO[self.model]
        except KeyError:
            params = {}

        if self._display_bytes:
            try:
                params['width_bytes'], params['height_bytes'] = map(int, self._display_bytes)
            except ValueError:
                pass

        return Display(**params)

    def parse(self):
        main, foma_or_comment = (self.useragent.split(' ', 1) + [None])[:2]
        if not foma_or_comment:
            # DoCoMo/1.0/R692i/c10
            self._parse_main(main)
        elif foma_or_comment[-1] != ')':
            raise exceptions.NoMatchingError(self)
        else:
            if foma_or_comment[0] == '(':
                # DoCoMo/1.0/P209is (Google CHTML Proxy/1.0)
                self.comment = foma_or_comment[1:-1]
                self._parse_main(main)
            else:
                # DoCoMo/2.0 N2001(c10;ser0123456789abcde;icc01234567890123456789)
                self._is_foma = True
                xxx, self.version = main.split('/')
                self._parse_foma(foma_or_comment)

    def _parse_main(self, main):
        """
        parse main part of HTTP_USER_AGENT string (not foma)
        """
        xxx, self.version, self.model, cache, rest = (main.split('/', 4) + [None, None, None, None])[:5]
        if self.model == 'SH505i2':
            self.model = 'SH505i'

        if cache:
            try:
                self.cache_size = int(cache[1:])
            except ValueError:
                raise exceptions.NoMatchingError(self)

        if rest:
            for value in rest.split('/'):
                if value in STATUS_SET:
                    self.status = value
                    continue

                if value.startswith('ser') and len(value) == 14:
                    self.serialnumber = value[3:]
                    continue

                if value.startswith('s'):
                    try:
                        self.bandwidth = int(value[1:])
                        continue
                    except ValueError:
                        pass

                matcher = DISPLAY_BYTES_RE.match(value)
                if matcher:
                    self._display_bytes = matcher.groups()

    def _parse_foma(self, foma):
        try:
            self.model, foma_params = foma.split('(', 1)
        except ValueError:
            raise exceptions.NoMatchingError(self)

        if self.model == 'MST_v_SH2101V':
            self.model = 'SH2101V'

        # for crawlers, such as
        # DoCoMo/2.0 N902iS(c100;TB;W24H12)(compatible; moba-crawler; http://crawler.dena.jp/)
        foma_params = foma_params.split(')', 1)[0]

        for value in foma_params.split(';'):
            if value in STATUS_SET:
                self.status = value
                continue

            if value.startswith('ser') and len(value) == 18:
                self.serialnumber = value[3:]
                continue

            if value.startswith('icc') and len(value) == 23:
                self.card_id = value[3:]
                continue

            if value.startswith('c'):
                try:
                    self.cache_size = int(value[1:])
                    continue
                except ValueError:
                    pass

            matcher = DISPLAY_BYTES_RE.match(value)
            if matcher:
                self._display_bytes = matcher.groups()
                continue

