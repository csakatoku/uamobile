# -*- coding: utf-8 -*-
from uamobile.base import UserAgent, Display

class NonMobileUserAgent(UserAgent):
    name = 'NonMobile'
    carrier = 'NonMobile'
    short_carrier = 'N'
    serialnumber = None

    def get_flash_version(self):
        """
        returns Flash Lite version.
        """
        return '3.1'
    flash_version = property(get_flash_version)

    def get_name(self):
        return 'NonMobile'

    def is_nonmobile(self):
        return True

    def supports_cookie(self):
        return True

    def make_display(self):
        """
        create a new Display object.
        """
        return Display()
