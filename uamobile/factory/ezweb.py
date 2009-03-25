# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.ezweb import EZwebUserAgent
from uamobile.parser import EZwebUserAgentParser

class EZwebUserAgentFactory(AbstractUserAgentFactory):
    device_class = EZwebUserAgent
    parser       = EZwebUserAgentParser()

