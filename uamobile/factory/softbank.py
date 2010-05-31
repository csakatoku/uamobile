# -*- coding: utf-8 -*-
from uamobile.factory.base import AbstractUserAgentFactory
from uamobile.softbank import SoftBankUserAgent
from uamobile.parser import CachingSoftBankUserAgentParser

class SoftBankUserAgentFactory(AbstractUserAgentFactory):
    device_class = SoftBankUserAgent
    parser       = CachingSoftBankUserAgentParser()

