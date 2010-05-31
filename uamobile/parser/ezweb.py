# -*- coding: utf-8 -*-
import re
from uamobile.parser.base import UserAgentParser


UP_BROWSER_COMMENT_RE = re.compile('^\((.*)\)$')

class EZwebUserAgentParser(UserAgentParser):
    def parse(self, useragent):
        if useragent.startswith('KDDI-'):
            return self._parse_kddi(useragent)
        else:
            return self._parse_upbrowser(useragent)

    def _parse_kddi(self, useragent):
        """
        Parse User-Agent like,
        - KDDI-TS21 UP.Browser/6.0.2.276 (GUI) MMP/1.1
        - KDDI-TS3A UP.Browser/6.2.0.11.2.1 (GUI) MMP/2.0, Mozilla/4.08 (MobilePhone; NMCS/3.3) NetFront/3.3
        """
        # Remove "KDDI-"
        useragent = useragent[5:]

        name = None
        version = None
        device_id, browser, opt, server = useragent.split(' ', 4)[:4]
        if server.endswith(','):
            server = server[:-1]

        name, version = browser.split('/')
        version = '%s %s' % (version, opt)

        return { 'xhtml_compliant': True,
                 'device_id'      : device_id,
                 'model'          : device_id,
                 'server'         : server,
                 'version'        : version,
                 'name'           : name,
                 'comment'        : None,
                 }

    def _parse_upbrowser(self, useragent):
        """
        Parse User-Agent like,
        - UP.Browser/3.01-HI01 UP.Link/3.4.5.2
        """
        browser, server, comment = (useragent.split(' ', 2) + [None, None])[:3]
        name, software = browser.split('/', 1)
        version, device_id = software.split('-', 1)
        if comment:
            comment = UP_BROWSER_COMMENT_RE.sub(lambda m: m.group(1), comment)

        return { 'xhtml_compliant': False,
                 'device_id'      : device_id,
                 'model'          : device_id,
                 'server'         : server,
                 'version'        : version,
                 'name'           : name,
                 'comment'        : comment,
                 }


class CachingEZwebUserAgentParser(EZwebUserAgentParser):
    def __init__(self):
        self._cache = {}

    def parse(self, useragent):
        try:
            return self._cache[useragent]
        except KeyError:
            result = super(CachingEZwebUserAgentParser, self).parse(useragent)
            self._cache[useragent] = result
            return result
