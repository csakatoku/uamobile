# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.docomo import DoCoMoUserAgent
from uamobile.parser import CachingDoCoMoUserAgentParser

class DoCoMoUserAgentFactory(AbstractUserAgentFactory):
    device_class = DoCoMoUserAgent
    parser       = CachingDoCoMoUserAgentParser()

