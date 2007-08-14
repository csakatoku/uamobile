# -*- coding: utf-8 -*-

class UserAgent(object):
    """
    Base class representing HTTTP user agent.
    """

    def __init__(self, environ):
        try:
            self.useragent = environ['HTTP_USER_AGENT']
        except KeyError, e:
            self.useragent = ''
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
        returns True if the agent is AirH'PHONE.
        """
        return False

    def is_wap1(self):
        return False

    def is_wap2(self):
        return False

    def is_nonmobile(self):
        return False

    def supports_cookie(self):
        """
        returns True if the agent supports HTTP cookie.
        """
        raise NotImplementedError

    def is_cookie_available(self):
        """
        returns True if the agent supports HTTP cookie.
        note that this methid is deprecated.
        """
        import warnings
        warnings.warn("The method 'is_cookie_available' is deprecated. Use supports_cookie instead.",
                      category=DeprecationWarning,
                      stacklevel=2)
        return self.supports_cookie()

class Display(object):
    """
    Display information for mobile devices.
    """

    def __init__(self, width=None, height=None, depth=None, color=None,
                 width_bytes=None, height_bytes=None):
        self.width = width or 0
        self.height = height or 0
        self.depth = depth or 0
        self.color = color or 0
        self.width_bytes = width_bytes
        self.height_bytes = height_bytes

    def is_qvga(self):
        return self.width >= 240

    def is_vga(self):
        return self.width >= 480
