# -*- coding: utf-8 -*-

class UserAgentError(Exception):
    pass

class NoMatchingError(UserAgentError):
    def __init__(self, ua=None, error=None):
        self.ua = ua
        self.error = error

    def __repr__(self):
        return '<uamobile.exceptions.NoMatchingError UserAgent:%s>' % self.ua

    def __str__(self):
        return 'Cannot not detect the useragent, "%s", original exception: %s' % (self.ua,
                                                                                  repr(self.error))
