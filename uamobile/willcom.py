# -*- coding: utf-8 -*-
from uamobile.base import UserAgent, Display

class WillcomUserAgent(UserAgent):
    name = 'WILLCOM'
    carrier = 'WILLCOM'
    short_carrier = 'W'

    def __init__(self, *args, **kwds):
        super(WillcomUserAgent, self).__init__(*args, **kwds)
        self.serialnumber = None
        self.model_version = None
        self.browser_version = None

    def supports_cookie(self):
        # TODO
        # I'm not sure All WILLCOM phones can handle HTTP cookie.
        return True

    def make_display(self):
        """
        create a new Display object.
        """
        return Display()

    def is_willcom(self):
        return True

    def is_airhphone(self):
        return True
