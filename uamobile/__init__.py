# -*- coding: utf-8 -*-
import re
from uamobile.nonmobile import NonMobileUserAgent as NonMobile
from uamobile.context import Context

__all__ = ['detect', 'Context', 'NonMobile']

DOCOMO_RE   = re.compile(r'^DoCoMo/\d\.\d[ /]')
SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)')
EZWEB_RE    = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')
WILLCOM_RE  = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);|^Mozilla/4\.0 \(compatible; MSIE (?:6\.0|4\.01); Windows CE; SHARP/WS\d+SH; PPC; \d+x\d+\)')

def detect(environ, context=None):
    """
    parse HTTP user agent string and detect a mobile device.
    """
    context = context or Context()
    try:
        useragent = environ['HTTP_USER_AGENT']
    except KeyError:
        return NonMobile(environ, context)

    if DOCOMO_RE.match(useragent):
        factory = context.docomo_factory()
    elif EZWEB_RE.match(useragent):
        factory = context.ezweb_factory()
    elif SOFTBANK_RE.match(useragent):
        factory = context.softbank_factory()
    elif WILLCOM_RE.match(useragent):
        factory = context.willcom_factory()
    else:
        return NonMobile(environ, context)

    return factory.create(environ, context)
