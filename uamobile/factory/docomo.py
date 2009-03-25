# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.docomo import DoCoMoUserAgent
from uamobile.parser import DoCoMoUserAgentParser

class DoCoMoUserAgentFactory(AbstractUserAgentFactory):
    device_class = DoCoMoUserAgent
    parser       = DoCoMoUserAgentParser()

