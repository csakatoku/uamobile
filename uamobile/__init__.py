# -*- coding: utf-8 -*-
import re
import uamobile.exceptions
from uamobile.nonmobile import NonMobileUserAgent as NonMobile
from uamobile.docomo import DoCoMoUserAgent as DoCoMo
from uamobile.ezweb import EZwebUserAgent as EZweb
from uamobile.softbank import SoftBankUserAgent as SoftBank
from uamobile.willcom import WillcomUserAgent as Willcom

__all__ = ['detect', 'NonMobile', 'DoCoMo', 'EZweb', 'SoftBank', 'Willcom']

DOCOMO_RE   = re.compile(r'^DoCoMo/\d\.\d[ /]')
SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)')
EZWEB_RE    = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')
WILLCOM_RE  = re.compile(r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);|^Mozilla/4\.0 \(compatible; MSIE (?:6\.0|4\.01); Windows CE; SHARP/WS\d+SH; PPC; \d+x\d+\)')

def detect(environ):
    """
    parse HTTP user agent string and detect a mobile device.
    """
    try:
        useragent = environ['HTTP_USER_AGENT']
    except KeyError:
        useragent = ''

    if DOCOMO_RE.match(useragent):
        device = DoCoMo(environ)
    elif EZWEB_RE.match(useragent):
        device = EZweb(environ)
    elif SOFTBANK_RE.match(useragent):
        device = SoftBank(environ)
    elif WILLCOM_RE.match(useragent):
        device = Willcom(environ)
    else:
        device = NonMobile(environ)

    try:
        device.parse()
    except exceptions.NoMatchingError, e:
        raise e
    except ValueError, e:
        raise exceptions.NoMatchingError(device, e)

    return device
