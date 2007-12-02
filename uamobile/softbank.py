# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display
import re

VODAFONE_VENDOR_RE = re.compile(r'V\d+([A-Z]+)')
JPHONE_VENDOR_RE = re.compile(r'J-([A-Z]+)')

class SoftBankUserAgent(UserAgent):
    carrier = 'SoftBank'
    short_carrier = 'S'

    def __init__(self, *args, **kwds):
        UserAgent.__init__(self, *args, **kwds)
        self.model = ''
        self.packet_compliant = False
        self.serialnumber = None
        self.vendor = ''
        self.vendor_version = None
        self.java_info = {}
        self._is_3g = True
        self.msname = ''

    def supports_cookie(self):
        """
        returns True if the device supports HTTP Cookie.
        For more information, see
        http://www2.developers.softbankmobile.co.jp/dp/tool_dl/download.php?docid=119
        """
        return self.is_3g() or self.is_type_w()

    def is_softbank(self):
        return True

    def is_vodafone(self):
        return True

    def is_jphone(self):
        return True

    def is_3g(self):
        return self._is_3g

    def is_type_c(self):
        """
        returns True if the type is C.
        """
        return not self._is_3g and (self.version.startswith('3.') or self.version.startswith('2.'))

    def is_type_p(self):
        """
        returns True if the type is P.
        """
        return not self._is_3g and self.version.startswith('4.')

    def is_type_w(self):
        """
        returns True if the type is W.
        """
        return not self._is_3g and self.version.startswith('5.')

    def get_jphone_uid(self):
        """
        returns the x-jphone-uid
        for the information about x-jphone-uid, see
        http://developers.softbankmobile.co.jp/dp/tool_dl/web/tech.php
        """
        try:
            return self.environ['HTTP_X_JPHONE_UID']
        except KeyError:
            return None
    jphone_uid = property(get_jphone_uid)

    def parse(self):
        ua = self.useragent.split(' ')

        carrier = ua[0]
        if carrier.startswith('SoftBank') or carrier.startswith('Vodafone'):
            self._parse_vodaphone(ua)
        elif carrier.startswith('J-PHONE'):
            self._parse_jphone(ua)
        elif carrier.startswith('MOT-'):
            self._parse_motorola(ua)
        else:
            raise exceptions.NoMatchingError(self)

        try:
            self.msname = self.environ['HTTP_X_JPHONE_MSNAME']
        except KeyError, e:
            self.msname = None

    def make_display(self):
        """
        create a new Display object.
        """
        try:
            width, height = map(int, self.environ['HTTP_X_JPHONE_DISPLAY'].split('*', 1))
        except (KeyError, ValueError, AttributeError):
            width = None
            height = None

        try:
            color_string = self.environ['HTTP_X_JPHONE_COLOR']
            try:
                color = color_string.startswith('C')
            except AttributeError:
                color = False

            try:
                depth = int(color_string[1:])
            except (ValueError, TypeError):
                depth = 0
        except KeyError:
            color = False
            depth = 0

        return Display(width=width, height=height, color=color, depth=depth)

    def _parse_vodaphone(self, ua):
        self.packet_compliant = True

        # Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V702NK/NKJ001/SN123456789012345 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V802SE/SEJ001/SN123456789012345 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 Configuration/CLDC-1.1

        (self.name,
         self.version,
         self.model,
         vendor_version,
         serial) = (ua[0].split('/') + [None, None, None, None])[:5]

        if serial:
            if not serial.startswith('SN'):
                raise exceptions.NoMatchingError(self)
            self.serialnumber = serial[2:]

        if not vendor_version:
            raise exceptions.NoMatchingError(self)
        self.vendor, self.vendor_version = vendor_version[:-4], vendor_version[-4:]

        self.java_info.update([x.split('/') for x in ua[2:]])

    def _parse_jphone(self, ua):
        self._is_3g = False
        if len(ua) > 1 and not ua[1].startswith('('):
            # J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0
            self.packet_compliant = True
            (self.name,
             self.version,
             self.model,
             serial) = (ua[0].split('/') + [None, None, None])[:4]
            if serial:
                if not serial.startswith('SN'):
                    raise exceptions.NoMatchingError(self)
                self.serialnumber = serial[2:]

            try:
                self.vendor, self.vendor_version = ua[1].split('/')
            except ValueError, e:
                raise ValueError(str(ua))
            self.java_info.update([x.split('/') for x in ua[2:]])
        else:
            # J-PHONE/2.0/J-DN02
            # J-PHONE/2.0/J-SH03 (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)
            self.name, self.version, self.model = ua[0].split('/')
            if self.model:
                matcher = VODAFONE_VENDOR_RE.match(self.model)
                if matcher:
                    self.vendor = matcher.group(1)
                else:
                    matcher = JPHONE_VENDOR_RE.match(self.model)
                    if matcher:
                        self.vendor = matcher.group(1)

    def _parse_motorola(self, ua):
        """
        parse HTTP_USER_AGENT string for the Motorola 3G agent
        """
        self.packet_compliant = True
        self.vendor = 'MOT'

        # MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
        name, self.vendor_version = ua[0].split('/')
        self.model = name[name.rindex('-')+1:]

        self.java_info.update([x.split('/') for x in ua[2:]])
