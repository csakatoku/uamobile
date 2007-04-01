# -*- coding: utf-8 -*-

class MockWSGIEnviron(object):
    def __init__(self, ua, headers=None):
        self._headers = { 'HTTP_USER_AGENT': ua }
        if headers:
            self._headers.update(headers)

    def __getitem__(self, key):
        return self._headers[key]

    def get(self, key, default=None):
        return self._headers.get(key, default)

    def getheader(self, *args, **kwds):
        return self._headers.get(*args, **kwds)

msg = lambda ua, x, y: 'UserAgent "%s": "%s" expected, got "%s".' % (ua.useragent, y, x)
