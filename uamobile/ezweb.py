# -*- coding: utf-8 -*-
from uamobile import exceptions
from uamobile.base import UserAgent, Display

import re

UP_BROWSER_COMMENT_RE = re.compile('^\((.*)\)$')

class EZwebUserAgent(UserAgent):
    carrier = 'EZweb'
    short_carrier = 'E'

    def __init__(self, *args, **kwds):
        UserAgent.__init__(self, *args, **kwds)
        self._comment = None
        self._display = None
        self.xhtml_compliant = False
        self.model = ''
        self.device_id = ''
        self.server = ''

    def supports_cookie(self):
        return True

    def parse(self):
        if self.useragent.startswith('KDDI-'):
            # KDDI-TS21 UP.Browser/6.0.2.276 (GUI) MMP/1.1
            # KDDI-TS3A UP.Browser/6.2.0.11.2.1 (GUI) MMP/2.0, Mozilla/4.08 (MobilePhone; NMCS/3.3) NetFront/3.3
            useragent = self.useragent[5:]
            self.xhtml_compliant = True
            self.device_id, browser, opt, self.server = useragent.split(' ', 4)[:4]
            if self.server.endswith(','):
                self.server = self.server[:-1]
            self._name, version = browser.split('/')
            self.version = '%s %s' % (version, opt)
        else:
            # UP.Browser/3.01-HI01 UP.Link/3.4.5.2
            browser, self.server, comment = (self.useragent.split(' ', 2) + [None, None])[:3]
            self._name, software = browser.split('/', 1)
            self.version, self.device_id = software.split('-', 1)
            if comment:
                self._comment = UP_BROWSER_COMMENT_RE.sub(r'\1', comment)

        self.model = self.device_id

    def make_display(self):
        """
        create a Display object.
        """
        if self._display is None:
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

            self._display = Display(width=width, height=height, color=color, depth=depth)
        return self._display

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

    def get_comment(self):
        """
        returns comment link 'Google WAP Proxy/1.0'.
        if no comment, then returns None.
        """
        return self._comment
    comment = property(get_comment)

    def is_xhtml_compliant(self):
        """
        returns whether it's XHTML compliant or not.
        """
        return self.xhtml_compliant

    def is_win(self):
        """
        returns whether the agent is CDMA 1X WIN or not.
        """
        return self._device_id[2:1] == '3'

    def is_wap1(self):
        return not self.is_wap2()

    def is_wap2(self):
        return self.xhtml_compliant
