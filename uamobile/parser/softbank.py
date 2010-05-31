# -*- coding: utf-8 -*-
import re
from uamobile.parser.base import UserAgentParser


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

        info = dict([x.split('/', 1) for x in ua[1:] if x])

        return { 'packet_compliant': True,
                 'version'         : version,
                 'model'           : model,
                 'vendor'          : vendor,
                 'vendor_version'  : vendor_version,
                 'serialnumber'    : serialnumber,
                 'info'            : info,
                 '_is_3g'          : True,
                 }

    def _parse_jphone(self, ua):
        serialnumber = None
        vendor = None
        vendor_version = None
        info = {}

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

            info.update([x.split('/', 1) for x in ua[1:]])
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
                 'info'            : info,
                 '_is_3g'          : False,
                 }

    def _parse_motorola(self, ua):
        """
        parse HTTP_USER_AGENT string for the Motorola 3G agent
        """
        # MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
        name, vendor_version = ua[0].split('/')
        model = name[name.rindex('-')+1:]

        info = dict([x.split('/', 1) for x in ua[1:]])

        return { 'packet_compliant': True,
                 'vendor'          : 'MOT',
                 'vendor_version'  : vendor_version,
                 'model'           : model,
                 'info'            : info,
                 '_is_3g'          : True,
                 }


class CachingSoftBankUserAgentParser(SoftBankUserAgentParser):
    def __init__(self):
        self._cache = {}

    def parse(self, useragent):
        try:
            return self._cache[useragent]
        except KeyError:
            result = super(CachingSoftBankUserAgentParser, self).parse(useragent)
            if result.get('serialnumber') is None:
                self._cache[useragent] = result
            return result
