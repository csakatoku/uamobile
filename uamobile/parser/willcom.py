# -*- coding: utf-8 -*-
import re
from uamobile.parser.base import UserAgentParser

WILLCOM_RE = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);(.*)\)')
WILLCOM_CACHE_RE = re.compile(r'^[Cc](\d+)')
WINDOWS_CE_RE = re.compile(r'^Mozilla/4\.0 \((.*)\)')

class WillcomUserAgentParser(UserAgentParser):
    def parse(self, useragent):
        if useragent.startswith('Mozilla/4.0'):
            return self._parse_windows_ce(useragent)

        matcher = WILLCOM_RE.match(useragent)
        if not matcher:
            return {}

        (vendor,
         model,
         model_version,
         browser_version,
         cache) = matcher.group(1).split('/')

        cache_size = None
        if cache and cache.lower().startswith('c'):
            try:
                cache_size = int(cache[1:])
            except ValueError:
                pass

        return { 'vendor'         : vendor,
                 'model'          : model,
                 'model_version'  : model_version,
                 'browser_version': browser_version,
                 'cache_size'     : cache_size,
                 }

    def _parse_windows_ce(self, useragent):
        # Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)
        matcher = WINDOWS_CE_RE.match(useragent)
        if not matcher:
            return {}

        try:
            _, browser_version, os, vendor_and_model, arch, width_and_height = matcher.group(1).split(';')
            vendor, model = vendor_and_model.strip().split('/')

            return { 'vendor'         : vendor.strip(),
                     'model'          : model.strip(),
                     'browser_version': browser_version.strip(),
                     'cache_size'     : None,
                     'os'             : os.strip(),
                     'arch'           : arch.strip(),
                     'display_bytes'  : width_and_height.strip(),
                     }
        except ValueError, e:
            return {}


class CachingWillcomUserAgentParser(WillcomUserAgentParser):
    def __init__(self):
        self._cache = {}

    def parse(self, useragent):
        try:
            return self._cache[useragent]
        except KeyError:
            result = super(CachingWillcomUserAgentParser, self).parse(useragent)
            self._cache[useragent] = result
            return result
