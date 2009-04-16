# -*- coding: utf-8 -*-
from uamobile.base import UserAgent, Display

class EZwebUserAgent(UserAgent):
    carrier = 'EZweb'
    short_carrier = 'E'

    def supports_cookie(self):
        return True

    def make_display(self):
        """
        create a Display object.
        """
        env = self.environ
        try:
            width, height = map(int, env['HTTP_X_UP_DEVCAP_SCREENPIXELS'].split(',', 1))
        except (KeyError, ValueError), e:
            width = None
            height = None

        try:
            color = env['HTTP_X_UP_DEVCAP_ISCOLOR'] == '1'
        except KeyError:
            color = False

        try:
            sd = env['HTTP_X_UP_DEVCAP_SCREENDEPTH'].split(',', 1)
            depth = sd[0] and (2 ** int(sd[0])) or 0
        except (KeyError, ValueError):
            depth = None

        return Display(width=width, height=height, color=color, depth=depth)

    def is_ezweb(self):
        return True

    def get_serialnumber(self):
        """
        return the EZweb subscriber ID.
        if no subscriber ID is available, returns None.
        """
        try:
            return self.environ['HTTP_X_UP_SUBNO']
        except KeyError:
            return None
    serialnumber = property(get_serialnumber)

    def is_xhtml_compliant(self):
        """
        returns whether it's XHTML compliant or not.
        """
        return self.xhtml_compliant

    def is_win(self):
        """
        returns whether the agent is CDMA 1X WIN or not.
        """
        return self.device_id[2:3] == '3'

    def is_wap1(self):
        return not self.is_wap2()

    def is_wap2(self):
        return self.xhtml_compliant
