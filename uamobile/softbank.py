# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display
import re

CARRIER_RE = re.compile(r'^(?:(SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)')

MODEL_VERSION_RE = re.compile(r'^([a-z]+)((?:[a-z]|\d){4})$', re.I)

SERIALNUMBER_RE = re.compile(r'^SN(.+)')

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

    def is_cookie_available(self):
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
        if self._is_3g:
            return False

        if not re.match(r'^[32]\.', self.version):
            return False

        return True

    def is_type_p(self):
        """
        returns True if the type is P.
        """
        if self._is_3g:
            return False

        if not re.match(r'^4\.', self.version):
            return False

        return True

    def is_type_w(self):
        """
        returns True if the type is W.
        """
        if self._is_3g:
            return False

        if not re.match(r'^5\.', self.version):
            return False

        return True

    def parse(self):
        ua = self.useragent.split(' ')
        
        matcher = CARRIER_RE.match(ua[0])
        carrier = matcher.group(1) or 'Motorola'
        { 'Vodafone': self._parse_vodaphone,
          'SoftBank' : self._parse_vodaphone,
          'J-PHONE'  : self._parse_jphone,
          'Motorola' : self._parse_motorola }[carrier](ua)

        self.msname = self.getheader('HTTP_X_JPHONE_MSNAME')

    def make_display(self):
        """
        create a new Display object.
        """       
        try:
            display = self.environ['HTTP_X_JPHONE_DISPLAY']            
            width, height = map(int, display.split('*'))
        except (KeyError, ValueError):
            return Display()

        color = False
        depth = 0
        try:
            color_string = self.environ['HTTP_X_JPHONE_COLOR']
            matcher = re.match(r'^([CG])(\d+)$', color_string)
            if matcher:
                color = (matcher.group(1) == 'C')
                try:
                    depth = int(matcher.group(2))
                except ValueError:
                    pass
        except KeyError:
            pass

        return Display(width=width, height=height, color=color, depth=depth)

    def _parse_vodaphone(self, ua):
        self.packet_compliant = True

        # Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V702NK/NKJ001/SN123456789012345 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1
        # Vodafone/1.0/V802SE/SEJ001/SN123456789012345 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 Configuration/CLDC-1.1

        (self.name,
         self.version,
         self.model,
         model_version,
         serial) = (ua[0].split('/') + [None, None, None, None])[:5]

        if serial:
            matcher = SERIALNUMBER_RE.match(serial)
            if not matcher:
                raise exceptions.NoMatchingError(self)
            self.serialnumber = matcher.group(1)

        matcher = MODEL_VERSION_RE.match(model_version)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        self.vendor = matcher.group(1)
        self.vendor_version = matcher.group(2)

        self.java_info.update([x.split('/') for x in ua[2:]])

    def _parse_jphone(self, ua):
        self._is_3g = False
        if len(ua) > 1:
            # J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0
            self.packet_compliant = True
            (self.name,
             self.version,
             self.model,
             serial) = (ua[0].split('/') + [None, None, None])[:4]
            if serial:
                matcher = SERIALNUMBER_RE.match(serial)
                if not matcher:
                    raise exceptions.NoMatchingError(self)
                self.serialnumber = matcher.group(1)

            self.vendor, self.vendor_version = ua[1].split('/')
            self.java_info.update([x.split('/') for x in ua[2:]])            
        else:
            # J-PHONE/2.0/J-DN02
            self.name, self.version, self.model = ua[0].split('/')
            if self.model:
                matcher = re.match(r'V\d+([A-Z]+)', self.model)
                if matcher:
                    self.vendor = matcher.group(1)
                else:
                    matcher = re.match(r'J-([A-Z]+)', self.model)
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
