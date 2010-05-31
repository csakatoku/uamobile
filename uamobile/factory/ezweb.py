# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.ezweb import EZwebUserAgent
from uamobile.parser import CachingEZwebUserAgentParser

class EZwebUserAgentFactory(AbstractUserAgentFactory):
    device_class = EZwebUserAgent
    parser       = CachingEZwebUserAgentParser()

