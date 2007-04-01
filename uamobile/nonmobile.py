# -*- coding: utf-8 -*-
from uamobile import exceptions, UserAgent

class NonMobileUserAgent(UserAgent):
    name = 'NonMobile'
    carrier = 'NonMobile'
    short_carrier = 'N'

    def get_name(self):
        return 'NonMobile'

    def is_nonmobile(self):
        return True

    def parse(self):
        pass

    def make_display(self):
        raise NotImplementedError
