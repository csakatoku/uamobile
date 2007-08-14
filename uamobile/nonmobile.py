# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display

class NonMobileUserAgent(UserAgent):
    name = 'NonMobile'
    carrier = 'NonMobile'
    short_carrier = 'N'

    def get_name(self):
        return 'NonMobile'

    def is_nonmobile(self):
        return True

    def supports_cookie(self):
        return True

    def parse(self):
        pass

    def make_display(self):
        """
        create a new Display object.
        """
        return Display()

    serialnumber = property(lambda _: None)
