# -*- coding: utf-8 -*-
import re
from uamobile.parser.base import UserAgentParser


DOCOMO_STATUS_SET = ('TB', 'TC', 'TD', 'TJ')

DOCOMO_VENDOR_RE = re.compile(r'([A-Z]+)\d')

FOMA_SERIES_4DIGITS_RE = re.compile(r'\d{4}')
FOMA_SERIES_3DIGITS_RE = re.compile(r'(\d{3}i|\d{2}[ABC][23]?)')

DOCOMO_COMMENT_RE = re.compile(r'\((.+?)\)')
DOCOMO_DISPLAY_BYTES_RE = re.compile(r'^W(\d+)H(\d+)$')

DOCOMO_HTML_VERSION_LIST = [
        (re.compile('[DFNP]501i'), '1.0'),
        (re.compile('502i|821i|209i|651|691i|(?:F|N|P|KO)210i|^F671i$'), '2.0'),
        (re.compile('(?:D210i|SO210i)|503i|211i|SH251i|692i|200[12]|2101V'), '3.0'),
        (re.compile('504i|251i|^F671iS$|212i|2051|2102V|661i|2701|672i|SO213i|850i'), '4.0'),
        (re.compile('eggy|P751v'), '3.2'),
        (re.compile('505i|252i|900i|506i|880i|253i|P213i|901i|700i|851i$|701i|881i|^SA800i$|600i|^L601i$|^M702i(?:S|G)$|^L602i$'), '5.0'),
        (re.compile('902i|702i|851iWM|882i|883i$|^N601i$|^D800iDS$|^P70[34]imyu$'), '6.0'),
        (re.compile('883iES|903i|703i|904i|704i'), '7.0'),
        (re.compile('905i|705i'), '7.1'),
        (re.compile('906i|[01][0-9]A[23]?'), '7.2'),
        ]

def _get_docomo_html_version(model):
    """
    returns supported HTML version like '3.0'.
    if unkwon, return None.
    """
    for pattern, value in DOCOMO_HTML_VERSION_LIST:
        if pattern.search(model):
            return value
    return None

class DoCoMoUserAgentParser(UserAgentParser):
    def parse(self, useragent):
        if not useragent.startswith('DoCoMo/'):
            # this useragent isn't one of docomo in the first place
            return {}

        main, foma_or_comment = (useragent.split(' ', 1) + [None])[:2]

        if not foma_or_comment:
            # DoCoMo/1.0/R692i/c10
            res = self._parse_main(main)
        else:
            if foma_or_comment[0] == '(':
                # DoCoMo/1.0/P209is (Google CHTML Proxy/1.0)
                res = self._parse_main(main)
                res['comment'] = foma_or_comment[1:-1]
            else:
                # DoCoMo/2.0 N2001(c10;ser0123456789abcde;icc01234567890123456789)
                res = self._parse_foma(foma_or_comment)
                _, version = main.split('/')
                res['version'] = version

        model = res.get('model', '')

        # get vender code
        matcher = DOCOMO_VENDOR_RE.match(model)
        if matcher:
            res['vendor'] = matcher.group(1)

        return res

    def _parse_main(self, main):
        """
        parse main part of HTTP_USER_AGENT string (not foma)
        """
        _, version, model, cache, rest = (main.split('/', 4) + [None, None, None, None])[:5]
        if model == 'SH505i2':
            model = 'SH505i'

        # Get series
        if model == 'P651ps':
            series = '651'
        else:
            matcher = FOMA_SERIES_3DIGITS_RE.search(model)
            if matcher:
                series = matcher.group(1)
            else:
                series = None

        params = { 'model': model,
                   'version': version,
                   'status' : None,
                   'ser'    : None,
                   's'      : None,
                   'display_bytes': None,
                   'series' : series,
                   'html_version' : _get_docomo_html_version(model),
                   }
        if cache:
            try:
                params['c'] = int(cache[1:])
            except ValueError:
                pass

        if rest:
            for value in rest.split('/'):
                if value in DOCOMO_STATUS_SET:
                    params['status'] = value
                    continue

                if value.startswith('ser') and len(value) == 14:
                    params['ser'] = value[3:]
                    continue

                if value.startswith('s'):
                    try:
                        params['s'] = int(value[1:])
                        continue
                    except ValueError:
                        pass

                matcher = DOCOMO_DISPLAY_BYTES_RE.match(value)
                if matcher:
                    params['display_bytes'] = (int(matcher.group(1)), int(matcher.group(2)))
                    continue

        return params

    def _parse_foma(self, foma):
        # remove comment
        matcher = DOCOMO_COMMENT_RE.search(foma)
        if matcher:
            # use only first comment and ignore the rest
            # such as,
            # "DoCoMo/2.0 P900i(c100;TB;W24H11)(compatible; ichiro/mobile goo; +http://help.goo.ne.jp/door/crawler.html)"
            foma_params = matcher.group(1)
        else:
            foma_params = ''

        model = foma.split('(', 1)[0]

        if model == 'MST_v_SH2101V':
            model = 'SH2101V'

        # Get FOMA series number
        if FOMA_SERIES_4DIGITS_RE.search(model):
            ## agents such as "DoCoMo/2.0 P2102V(c100;TB)"
            series = 'FOMA'
        else:
            matcher = FOMA_SERIES_3DIGITS_RE.search(model)
            if matcher:
                series = matcher.group(1)
            else:
                series = None

        params = { 'model'        : model,
                   'status'       : None,
                   'ser'          : None,
                   'icc'          : None,
                   'display_bytes': None,
                   'series'       : series,
                   'html_version' : _get_docomo_html_version(model),
                   }
        for value in foma_params.split(';'):
            if value in DOCOMO_STATUS_SET:
                params['status'] = value
                continue

            if value.startswith('ser') and len(value) == 18:
                params['ser'] = value[3:]
                continue

            if value.startswith('icc') and len(value) == 23:
                params['icc'] = value[3:]
                continue

            if value.startswith('c'):
                try:
                    params['c'] = int(value[1:])
                    continue
                except ValueError:
                    pass

            matcher = DOCOMO_DISPLAY_BYTES_RE.match(value)
            if matcher:
                params['display_bytes'] = (int(matcher.group(1)), int(matcher.group(2)))
                continue

        return params


class CachingDoCoMoUserAgentParser(DoCoMoUserAgentParser):
    def __init__(self):
        self._cache = {}

    def parse(self, useragent):
        try:
            return self._cache[useragent]
        except KeyError:
            result = super(CachingDoCoMoUserAgentParser, self).parse(useragent)
            if result.get('ser') is None and result.get('icc') is None:
                self._cache[useragent] = result
            return result
