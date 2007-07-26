# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display
import re

WILLCOM_RE = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);(.*)\)')
CACHE_RE = re.compile(r'^[Cc](\d+)')
WINDOWS_CE_RE = re.compile(r'^Mozilla/4\.0 \((.*)\)')

class WillcomUserAgent(UserAgent):
    name = 'WILLCOM'
    carrier = 'WILLCOM'
    short_carrier = 'W'

    def __init__(self, *args, **kwds):
        UserAgent.__init__(self, *args, **kwds)
        self.vendor = ''
        self.model = ''
        self.model_version = ''
        self.browser_version = ''
        self.cache_size = None

        # WILLCOM does not support the serial number of a device
        # except official web sites?
        self.serialnumber = None        

    def is_cookie_available(self):
        # TODO
        # I'm not sure All WILLCOM phones can handle HTTP cookie.
        return True

    def parse(self):
        if self.useragent.startswith('Mozilla/4.0'):
            return self._parse_windows_ce()

        matcher = WILLCOM_RE.match(self.useragent)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        (self.vendor,
         self.model,
         self.model_version,
         self.browser_version,
         cache) = matcher.group(1).split('/')
        
        matcher = CACHE_RE.match(cache)
        if not matcher:
            raise NoMatchingError(self)

        self.cache_size = int(matcher.group(1))

    def _parse_windows_ce(self):
        #Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)
        matcher = WINDOWS_CE_RE.match(self.useragent)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        try:
            xx, ie, xxx, vendor_and_model, xxxx, width_and_height = matcher.group(1).split(';')
            self.vendor, self.model = vendor_and_model.strip().split('/')
        except ValueError, e:
            raise exceptions.NoMatchingError(self)

    def make_display(self):
        """
        create a new Display object.
        """
        return Display()

    def is_willcom(self):
        return True

    def is_airhphone(self):
        return True
