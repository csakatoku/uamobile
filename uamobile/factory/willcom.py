# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.willcom import WillcomUserAgent
from uamobile.parser import WillcomUserAgentParser

class WillcomUserAgentFactory(AbstractUserAgentFactory):
    device_class = WillcomUserAgent
    parser       = WillcomUserAgentParser()

