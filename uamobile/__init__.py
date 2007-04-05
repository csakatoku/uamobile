# -*- coding: utf-8 -*-
import re
import uamobile.exceptions
from uamobile.nonmobile import NonMobileUserAgent as NonMobile
from uamobile.docomo import DoCoMoUserAgent as DoCoMo
from uamobile.ezweb import EZwebUserAgent as EZweb
from uamobile.softbank import SoftbankUserAgent as SoftBank
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

def detect(environ, lazy=False):
    """
    parse HTTP user agent string and detect a mobile device.   
    """
    try:
        matcher = MOBILE_RE.match(environ['HTTP_USER_AGENT'])
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
