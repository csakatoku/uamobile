# -*- coding: utf-8 -*-

class AbstractUserAgentFactory(object):
    parser = None
    device_class = None

    def create(self, environ, context):
        params = self.parser.parse(environ.get('HTTP_USER_AGENT', ''))
        device = self.device_class(environ, context)
        for k, v in params.items():
            setattr(device, k, v)
        return device
