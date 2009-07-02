# -*- coding: utf-8 -*-
import re

class UserAgentParser(object):
    def parse(self, useragent):
        raise NotImplementedError()

###################################
# docomo
###################################

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


###################################
# EZWeb
###################################

UP_BROWSER_COMMENT_RE = re.compile('^\((.*)\)$')

class EZwebUserAgentParser(UserAgentParser):
    def parse(self, useragent):
        if useragent.startswith('KDDI-'):
            return self._parse_kddi(useragent)
        else:
            return self._parse_upbrowser(useragent)

    def _parse_kddi(self, useragent):
        """
        Parse User-Agent like,
        - KDDI-TS21 UP.Browser/6.0.2.276 (GUI) MMP/1.1
        - KDDI-TS3A UP.Browser/6.2.0.11.2.1 (GUI) MMP/2.0, Mozilla/4.08 (MobilePhone; NMCS/3.3) NetFront/3.3
        """
        # Remove "KDDI-"
        useragent = useragent[5:]

        name = None
        version = None
        device_id, browser, opt, server = useragent.split(' ', 4)[:4]
        if server.endswith(','):
            server = server[:-1]

        name, version = browser.split('/')
        version = '%s %s' % (version, opt)

        return { 'xhtml_compliant': True,
                 'device_id'      : device_id,
                 'model'          : device_id,
                 'server'         : server,
                 'version'        : version,
                 'name'           : name,
                 'comment'        : None,
                 }

    def _parse_upbrowser(self, useragent):
        """
        Parse User-Agent like,
        - UP.Browser/3.01-HI01 UP.Link/3.4.5.2
        """
        browser, server, comment = (useragent.split(' ', 2) + [None, None])[:3]
        name, software = browser.split('/', 1)
        version, device_id = software.split('-', 1)
        if comment:
            comment = UP_BROWSER_COMMENT_RE.sub(lambda m: m.group(1), comment)

        return { 'xhtml_compliant': False,
                 'device_id'      : device_id,
                 'model'          : device_id,
                 'server'         : server,
                 'version'        : version,
                 'name'           : name,
                 'comment'        : comment,
                 }

###################################
# SoftBank
###################################

VODAFONE_VENDOR_RE = re.compile(r'V\d+([A-Z]+)')
JPHONE_VENDOR_RE = re.compile(r'J-([A-Z]+)')
SOFTBANK_CRAWLER_RE = re.compile(r'\([^)]+\)')

class SoftBankUserAgentParser(UserAgentParser):

    def parse(self, useragent):
        """
        parse the useragent which starts with "SoftBank", "Vodafone", "J-PHONE", or "MOT-".
        """
        # strip crawler infomation such as,
        # J-PHONE/2.0/J-SH03 (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)
        # Vodafone/1.0/V705SH (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)
        # SoftBank/1.0/913SH/SHJ001/SN000123456789000 Browser/NetFront/3.4 Profile/MIDP-2.0 (symphonybot1.froute.jp; +http://search.froute.jp/howto/crawler.html)
        ua = SOFTBANK_CRAWLER_RE.sub('', useragent)
        ua = ua.strip().split(' ')

        carrier = ua[0]
        if carrier.startswith('SoftBank') or carrier.startswith('Vodafone'):
            return self._parse_vodaphone(ua)
        elif carrier.startswith('J-PHONE'):
            return self._parse_jphone(ua)
        elif carrier.startswith('MOT-'):
            return self._parse_motorola(ua)
        else:
            return {}

    def _parse_vodaphone(self, ua):
        # Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V702NK/NKJ001/SN123456789012345 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V802SE/SEJ001/SN123456789012345 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V705SH (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)

        (name,
         version,
         model,
         vendor_info,
         serial) = (ua[0].split('/') + [None, None, None, None])[:5]

        serialnumber = None
        if serial and serial.startswith('SN'):
            serialnumber = serial[2:]

        if not vendor_info:
            vendor = None
            vendor_version = None
        else:
            vendor = vendor_info[:-4]
            vendor_version = vendor_info[-4:]

        java_info = dict([x.split('/') for x in ua[2:] if x])

        return { 'packet_compliant': True,
                 'version'         : version,
                 'model'           : model,
                 'vendor'          : vendor,
                 'vendor_version'  : vendor_version,
                 'serialnumber'    : serialnumber,
                 'java_info'       : java_info,
                 '_is_3g'          : True,
                 }

    def _parse_jphone(self, ua):
        serialnumber = None
        vendor = None
        vendor_version = None
        java_info = {}

        if len(ua) > 1:
            # J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0
            packet_compliant = True

            (name,
             version,
             model,
             serial) = (ua[0].split('/') + [None, None, None])[:4]
            if serial and serial.startswith('SN'):
                serialnumber = serial[2:]

            try:
                vendor, vendor_version = ua[1].split('/')
            except ValueError, e:
                pass

            java_info.update([x.split('/') for x in ua[2:]])
        else:
            # J-PHONE/2.0/J-DN02
            packet_compliant = False

            name, version, model = ua[0].split('/')
            if model:
                matcher = VODAFONE_VENDOR_RE.match(model)
                if matcher:
                    vendor = matcher.group(1)
                else:
                    matcher = JPHONE_VENDOR_RE.match(model)
                    if matcher:
                        vendor = matcher.group(1)

        return { 'packet_compliant': packet_compliant,
                 'version'         : version,
                 'model'           : model,
                 'vendor'          : vendor,
                 'vendor_version'  : vendor_version,
                 'serialnumber'    : serialnumber,
                 'java_info'       : java_info,
                 '_is_3g'          : False,
                 }

    def _parse_motorola(self, ua):
        """
        parse HTTP_USER_AGENT string for the Motorola 3G agent
        """
        # MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
        name, vendor_version = ua[0].split('/')
        model = name[name.rindex('-')+1:]

        java_info = dict([x.split('/') for x in ua[2:]])

        return { 'packet_compliant': True,
                 'vendor'          : 'MOT',
                 'vendor_version'  : vendor_version,
                 'model'           : model,
                 'java_info'       : java_info,
                 '_is_3g'          : True,
                 }



###################################
# WILLCOM
###################################

WILLCOM_RE = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);(.*)\)')
WILLCOM_CACHE_RE = re.compile(r'^[Cc](\d+)')
WINDOWS_CE_RE = re.compile(r'^Mozilla/4\.0 \((.*)\)')

class WillcomUserAgentParser(UserAgentParser):
    def parse(self, useragent):
        if useragent.startswith('Mozilla/4.0'):
            return self._parse_windows_ce(useragent)

        matcher = WILLCOM_RE.match(useragent)
        if not matcher:
            return {}

        (vendor,
         model,
         model_version,
         browser_version,
         cache) = matcher.group(1).split('/')

        cache_size = None
        if cache and cache.lower().startswith('c'):
            try:
                cache_size = int(cache[1:])
            except ValueError:
                pass

        return { 'vendor'         : vendor,
                 'model'          : model,
                 'model_version'  : model_version,
                 'browser_version': browser_version,
                 'cache_size'     : cache_size,
                 }

    def _parse_windows_ce(self, useragent):
        # Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)
        matcher = WINDOWS_CE_RE.match(useragent)
        if not matcher:
            return {}

        try:
            _, browser_version, os, vendor_and_model, arch, width_and_height = matcher.group(1).split(';')
            vendor, model = vendor_and_model.strip().split('/')

            return { 'vendor'         : vendor.strip(),
                     'model'          : model.strip(),
                     'browser_version': browser_version.strip(),
                     'cache_size'     : None,
                     'os'             : os.strip(),
                     'arch'           : arch.strip(),
                     'display_bytes'  : width_and_height.strip(),
                     }
        except ValueError, e:
            return {}


