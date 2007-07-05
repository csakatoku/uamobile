# -*- coding: utf-8 -*-
import re
import uamobile.exceptions
from uamobile.nonmobile import NonMobileUserAgent as NonMobile
from uamobile.docomo import DoCoMoUserAgent as DoCoMo
from uamobile.ezweb import EZwebUserAgent as EZweb
from uamobile.softbank import SoftBankUserAgent as SoftBank
from uamobile.willcom import WillcomUserAgent as Willcom

__all__ = ['detect', 'NonMobile', 'DoCoMo', 'EZweb', 'SoftBank', 'Willcom']

DOCOMO_RE = r'^DoCoMo/\d\.\d[ /]'
SOFTBANK_RE = r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)'
EZWEB_RE = r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/'
WILLCOM_RE = r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);'

MOBILE_RE = re.compile(r'(?:(%s)|(%s)|(%s)|(%s))' % (DOCOMO_RE,
                                                     SOFTBANK_RE,
                                                     EZWEB_RE,
                                                     WILLCOM_RE))

WILLCOM_WZERO3_RE = re.compile(r'^Mozilla/4\.0 \(compatible; MSIE (?:6\.0|4\.01); Windows CE; SHARP/WS\d+SH; PPC; \d+x\d+\)')

def detect(environ, lazy=False):
    """
    parse HTTP user agent string and detect a mobile device.   
    """
    try:
        useragent = environ['HTTP_USER_AGENT']
        matcher = MOBILE_RE.match(useragent)
        if matcher:
            g = matcher.groups()
            if g[0]:
                result = DoCoMo(environ)
            elif g[1]:
                result = SoftBank(environ)
            elif g[2]:
                result = EZweb(environ)
            else:
                result = Willcom(environ)
        else:
            if WILLCOM_WZERO3_RE.match(useragent):
                result = Willcom(environ)
            else:
                result = NonMobile(environ)

    except KeyError:
        result = NonMobile(environ)

    # Currently we does not support lazy evaluation.
    try:
        result.parse()
    except exceptions.NoMatchingError:
        raise
    #except ValueError, e:
    #    raise exceptions.NoMatchingError(result, e)
    
    return result
