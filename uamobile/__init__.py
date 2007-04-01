# -*- coding: utf-8 -*-
import re
import uamobile.exceptions

DOCOMO_RE = r'^DoCoMo/\d\.\d[ /]'
SOFTBANK_RE = r'^(?:(?:SoftBank|Vodafone|J-PHONE)/\d\.\d|MOT-)'
EZWEB_RE = r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/'
WILLCOM_RE = r'^Mozilla/3\.0\((?:DDIPOCKET|WILLCOM);'

MOBILE_RE = re.compile(r'(?:(%s)|(%s)|(%s)|(%s))' % (DOCOMO_RE,
                                                     SOFTBANK_RE,
                                                     EZWEB_RE,
                                                     WILLCOM_RE))

def detect(request, lazy=False):
    """
    parse HTTP user agent string and detect a mobile device.   
    """
    from uamobile.nonmobile import NonMobileUserAgent
    from uamobile.docomo import DoCoMoUserAgent
    from uamobile.ezweb import EZwebUserAgent
    from uamobile.softbank import SoftbankUserAgent
    from uamobile.willcom import WillcomUserAgent

    ua = request.getheader('HTTP_USER_AGENT')
    sub = 'NonMobile'

    matcher = MOBILE_RE.match(ua)
    if matcher:
        g = matcher.groups()

        if g[0]:
            result = DoCoMoUserAgent(request)
        elif g[1]:
            result = SoftbankUserAgent(request)
        elif g[2]:
            result = EZwebUserAgent(request)
        else:
            result = WillcomUserAgent(request)
    else:
        result = NonMobileUserAgent(request)

    # Currently we does not support lazy evaluation.
    try:
        result.parse()
    except exceptions.NoMatchingError:
        raise
    #except ValueError, e:
    #    raise exceptions.NoMatchingError(result, e)
    
    return result

    
class UserAgent(object):
    def __init__(self, environ):
        self.useragent = environ['HTTP_USER_AGENT']
        self.environ = environ
        self.version = ''

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.useragent)

    def __str__(self):
        return self.useragent

    def getheader(self, key, default=None):
        """
        Gets the header for the given key.
        """
        return self.environ.get(key, default)

    def get_display(self):
        """
        returns Display object.
        """
        return self.make_display()
    display = property(get_display)

    def make_display(self):
        raise NotImplementedError

    def is_docomo(self):
        """
        returns True if the agent is DoCoMo.
        """
        return False

    def is_ezweb(self):
        """
        returns True if the agent is EZweb.
        """
        return False

    def is_tuka(self):
        """
        returns True if the agent is TU-Ka.
        """
        return False

    def is_softbank(self):
        """
        returns True if the agent is Softbank.
        """
        return False

    def is_vodafone(self):
        """
        returns True if the agent is Vodafone (now SotBank).
        """
        return False

    def is_jphone(self):
        """
        returns True if the agent is J-PHONE (now softbank).
        """
        return False

    def is_willcom(self):
        """
        returns True if the agent is Willcom.
        """
        return False

    def is_airhphone(self):
        """
        returns True if the agent is AirH"PHONE.
        """
        return False

    def is_wap1(self):
        return False

    def is_wap2(self):
        return False

    def is_nonmobile(self):
        return False
