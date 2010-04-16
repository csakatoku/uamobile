# -*- coding: utf-8 -*-
import re
from uamobile.nonmobile import NonMobileUserAgent as NonMobile
from uamobile.context import Context

__version__ = '0.2.11'
__author__  = 'Chihiro Sakatoku <csakatoku@gmail.com>'

__all__ = ['detect_fast', 'detect', 'Context', 'NonMobile']

DOCOMO_RE   = re.compile(r'^DoCoMo/\d\.\d[ /]')
SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)')
EZWEB_RE    = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')
WILLCOM_RE  = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);|^Mozilla/4\.0 \(compatible; MSIE (?:6\.0|4\.01); Windows CE; SHARP/WS\d+SH; PPC; \d+x\d+\)')

def detect_fast(useragent):
    """
    return name of Japanese mobile carriers from a given useragent string.
    if the agent isn't mobile one, then returns 'nonmobile'.
    """
    if DOCOMO_RE.match(useragent):
        return "docomo"
    elif EZWEB_RE.match(useragent):
        return "ezweb"
    elif SOFTBANK_RE.match(useragent):
        return "softbank"
    elif WILLCOM_RE.match(useragent):
        return "willcom"
    else:
        return "nonmobile"

def detect(environ, context=None):
    """
    parse HTTP user agent string and detect a mobile device.
    """
    context = context or Context()
    try:
        ## if key 'HTTP_USER_AGENT' doesn't exist,
        ## we are not able to decide agent class in the first place.
        ## so raise KeyError to return NonMobile agent.
        carrier = detect_fast(environ['HTTP_USER_AGENT'])

        ## if carrier is 'nonmobile', raise KeyError intentionally
        factory_class = {
            'docomo'  : context.docomo_factory,
            'ezweb'   : context.ezweb_factory,
            'softbank': context.softbank_factory,
            'willcom' : context.willcom_factory,
            }[carrier]
        return factory_class().create(environ, context)
    except KeyError:
        return NonMobile(environ, context)
