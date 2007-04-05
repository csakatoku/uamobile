# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent

import re

COMMENT_RE = re.compile(r'^\((.*)\)$')

CACHE_RE = re.compile(r'^c(\d+)')

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
                         (re.compile('903i|703i'), '7.0')
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
        matcher = re.match(r'([A-Z]+)\d', self.model)
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
        if self._is_foma and re.search(r'(\d{4})', self.model):
            return 'FOMA'
    
        matcher = re.search(r'(\d{3}i)', self.model)
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
                matcher = re.match(r'^ser(\w{11})$', value)
                if matcher:
                    self.serialnumber = matcher.group(1)
                    continue

                matcher = re.match(r'^(T[CDBJ])$', value)
                if matcher:
                    self._status = matcher.group(1)

                matcher = re.match(r'^s(\d+)$', value)
                if matcher:
                    self.bandwidth = int(matcher.group(1))

                matcher = re.match(r'^W(\d+)H(\d+)$', value)
                if matcher:
                    self._display_bytes = '%s*%s' % (matcher.group(1),
                                                     matcher.group(2))

    def _parse_foma(self, foma):
        matcher = re.match(r'^([^(]+)', foma)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        self.model = matcher.group(1)
        if self.model == 'MST_v_SH2101V':
            self.model = 'SH2101V'

        matcher = re.match(r'^[^(]+\((.*?)\)$', foma)
        if matcher:
            for value in matcher.group(1).split(';'):
                # PHP version does not use the suffix '$'
                # Should we follow that?
                matcher = re.match(r'^c(\d+)$', value)
                if matcher:
                    self._cache_size = int(matcher.group(1))
                    continue
                
                matcher = re.match('^ser(\w{15})$', value)
                if matcher:
                    self.serialnumber = matcher.group(1)
                    continue

                matcher = re.match(r'^(T[CDBJ])$', value)
                if matcher:
                    self._status = matcher.group(1)
                    continue;

                matcher = re.match(r'^icc(\w{20})?$', value)
                if matcher:
                    self.card_id = matcher.group(1)
                    continue

                matcher = re.match(r'^W(\d+)H(\d+)$', value)
                if matcher:
                    self._display_bytes = '%s*%s' % (matcher.group(1),
                                                     matcher.group(2))
                    continue

                raise exceptions.NoMatchingError(self)

