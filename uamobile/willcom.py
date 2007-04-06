# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display
import re

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

    def parse(self):      
        matcher = re.match(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);(.*)\)', self.useragent)
        if not matcher:
            raise exceptions.NoMatchingError(self)

        (self.vendor,
         self.model,
         self.model_version,
         self.browser_version,
         cache) = matcher.group(1).split('/')
            
        matcher = re.match(r'^[Cc](\d+)', cache)
        if not matcher:
            raise NoMatchingError(self)

        self.cache_size = int(matcher.group(1))

    def make_display(self):
        """
        create a new Display object.
        """
        return Display()

    def is_willcom(self):
        return True

    def is_airhphone(self):
        return True
